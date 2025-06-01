import datasets
import datasets as ds
from datasets import Audio
import librosa
from transformers import WhisperFeatureExtractor
from transformers import WhisperTokenizer
from transformers import WhisperProcessor
from transformers import WhisperForConditionalGeneration
import torch
from dataclasses import dataclass
from typing import Any, Dict, List, Union
import evaluate
from transformers import Seq2SeqTrainingArguments
from transformers import Seq2SeqTrainer

model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-medium")
tokenizer = WhisperTokenizer.from_pretrained("openai/whisper-medium", language="Czech", task="transcribe")
processor = WhisperProcessor.from_pretrained("openai/whisper-medium", language="Czech", task="transcribe")
feature_extractor = WhisperFeatureExtractor.from_pretrained("openai/whisper-medium")

def extract_mel_features(audio_file):
    # Load the audio with librosa
    print(audio_file["path"])
    audio, sr = librosa.load(audio_file["path"], sr=16000)  # Ensure it’s at the correct sampling rate

    # Extract mel-spectrogram
    mel_spectrogram = librosa.feature.melspectrogram(audio, sr=sr, n_mels=80, fmax=8000)
    mel_spectrogram = librosa.power_to_db(mel_spectrogram)  # Convert to dB scale

    # Return the mel-spectrogram
    return mel_spectrogram

def preprocess_function(examples):
    # Extract features for each example
    print(examples["audio"])
    examples["input_features"] = [extract_mel_features(audio_file) for audio_file in examples["audio"]]
    return examples

def prepare_dataset(batch):
    # load and resample audio data from 48 to 16kHz
    audio = batch["audio"]

    # compute log-Mel input features from input audio array
    batch["input_features"] = feature_extractor(audio["array"], sampling_rate=audio["sampling_rate"]).input_features[0]

    # encode target text to label ids
    batch["labels"] = tokenizer(batch["sentence"]).input_ids
    return batch

@dataclass
class DataCollatorSpeechSeq2SeqWithPadding:
    processor: Any
    decoder_start_token_id: int

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        # split inputs and labels since they have to be of different lengths and need different padding methods
        # first treat the audio inputs by simply returning torch tensors
        input_features = [{"input_features": feature["input_features"]} for feature in features]
        batch = self.processor.feature_extractor.pad(input_features, return_tensors="pt")

        # get the tokenized label sequences
        label_features = [{"input_ids": feature["labels"]} for feature in features]
        # pad the labels to max length
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")

        # replace padding with -100 to ignore loss correctly
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        # if bos token is appended in previous tokenization step,
        # cut bos token here as it's append later anyways
        if (labels[:, 0] == self.decoder_start_token_id).all().cpu().item():
            labels = labels[:, 1:]

        batch["labels"] = labels

        return batch

def compute_metrics(pred):
    pred_ids = pred.predictions
    label_ids = pred.label_ids

    # replace -100 with the pad_token_id
    label_ids[label_ids == -100] = tokenizer.pad_token_id

    # we do not want to group tokens when computing the metrics
    pred_str = tokenizer.batch_decode(pred_ids, skip_special_tokens=True)
    label_str = tokenizer.batch_decode(label_ids, skip_special_tokens=True)

    pred_str = [s.lower().strip() for s in pred_str]
    label_str = [s.lower().strip() for s in label_str]

    wer = 100 * metric_wer.compute(predictions=pred_str, references=label_str)
    cer = 100 * metric_cer.compute(predictions=pred_str, references=label_str)

    return {"wer": wer, "cer": cer}

dataset_t = ds.load_dataset("csv", data_files=["/mnt/matylda6/xokruc00/training-scripts/mono_output.tsv"], delimiter="\t")
#dataset_t = ds.load_dataset("csv", data_files=["../clip-cutter/my_mono_output.tsv"], delimiter="\t")
dataset_t = dataset_t.remove_columns(["length"])
dataset_t = dataset_t.cast_column("audio", Audio(sampling_rate=16000))
split_dataset = dataset_t["train"].train_test_split(test_size=0.2, seed=42)

dataset_dict = ds.DatasetDict()

dataset_dict["train"] = split_dataset["train"].shuffle(seed=42)
dataset_dict["test"] = split_dataset["test"]

dataset_dict = dataset_dict.map(prepare_dataset, remove_columns=dataset_dict.column_names["train"], num_proc=1)

model.generation_config.language = "czech"
model.generation_config.task = "transcribe"

model.generation_config.forced_decoder_ids = None

data_collator = DataCollatorSpeechSeq2SeqWithPadding(
    processor=processor,
    decoder_start_token_id=model.config.decoder_start_token_id,
)

metric_wer = evaluate.load("wer")
metric_cer = evaluate.load("cer")

training_args = Seq2SeqTrainingArguments(
    output_dir="/mnt/matylda6/xokruc00/training-scripts/output/whisper-medium-cz-dia-v8/",  # change to a repo name of your choice
    #output_dir="./output/whisper-medium-cz-dia-v1/",  # change to a repo name of your choice
    per_device_train_batch_size=15,
    gradient_accumulation_steps=6,  # increase by 2x for every 2x decrease in batch size
    learning_rate=3e-5,
    warmup_steps=50,
    num_train_epochs=15,
    gradient_checkpointing=True,
    fp16=True,
    weight_decay=1e-6,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_strategy="epoch",
    per_device_eval_batch_size=8,
    predict_with_generate=True,
    generation_max_length=225,
    report_to=["tensorboard"],
    load_best_model_at_end=True,
    metric_for_best_model="wer",
    greater_is_better=False,
    push_to_hub=False,
    remove_unused_columns=False,
)

trainer = Seq2SeqTrainer(
    args=training_args,
    model=model,
    train_dataset=dataset_dict["train"],
    eval_dataset=dataset_dict["test"],
    data_collator=data_collator,
    compute_metrics=compute_metrics,
    tokenizer=processor.feature_extractor,
)

processor.save_pretrained(training_args.output_dir)
trainer.train()
