"""
    This script will load trained Whisper model from checkpoint and test it with test data.

    Yes, this script you can rewrite to be easier with huggingface library :)

    Author: Alexander Rastislav Okrucký <xokruc00@stud.fit.vutbr.cz>
"""

import csv

import datasets as ds
import torch
from datasets import Audio
from transformers import WhisperFeatureExtractor
from transformers import WhisperTokenizer
from transformers import WhisperProcessor
from transformers import WhisperForConditionalGeneration

model_path = "/mnt/matylda6/xokruc00/training-scripts/output/whisper-medium-cz-dia-v8/checkpoint-180"
tok_patth = "/mnt/matylda6/xokruc00/training-scripts/output/whisper-medium-cz-dia-v8/"

model = WhisperForConditionalGeneration.from_pretrained(model_path)
tokenizer = WhisperTokenizer.from_pretrained(tok_patth)
processor = WhisperProcessor.from_pretrained(tok_patth)
feature_extractor = WhisperFeatureExtractor.from_pretrained(tok_patth, sampling_rate=16000)

tsv_path = "/mnt/matylda6/xokruc00/training-scripts/mono_output.tsv"

dataset_t = ds.load_dataset("csv", data_files=[tsv_path], delimiter="\t")
dataset_t = dataset_t.remove_columns(["length"])
dataset_t = dataset_t.cast_column("audio", Audio(sampling_rate=16000))
#split_dataset = dataset_t["train"].train_test_split(test_size=int(1300), train_size=int(1))
split_dataset = dataset_t["train"].train_test_split(test_size=0.2, seed=42)
dataset_dict = ds.DatasetDict()

print(len(split_dataset["train"]))
print(len(split_dataset["test"]))

dataset_dict["train"] = split_dataset["train"]
dataset_dict["test"] = split_dataset["test"]

print(dataset_dict)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

transcriptions = []
index = 0
for sample in dataset_dict["test"]:
    inputs = processor(sample["audio"]["array"], return_tensors="pt")
    input_features = inputs.input_features.to(device)

    # Generate transcription
    with torch.no_grad():
        generated_ids = model.generate(input_features)

    transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    print(index)
    #print(transcription)
    path = split_dataset["test"][index]["audio"]["path"]
    #print(split_dataset["test"][index]["audio"]["path"])
    transcriptions.append([path,transcription])
    index += 1

print(transcriptions)
print(f"Total Transcriptions: {len(transcriptions)}")

with open("./output-wer.tsv", "w") as txt_file:
    csv.writer(txt_file, delimiter="\t").writerows(transcriptions)
