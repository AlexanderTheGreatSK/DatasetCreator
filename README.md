# Dataset Creator
***

This toolkit creates a dataset with aligned data, ready for fine-tuning ASR models.

![pipeline image](/imgs/pipeline.png)


![data transformation image](/imgs/data-processing.png)

# Input limitations
Each audio is expected to be in a different directory, with one transcription file.
If you have more transcription files for one audio file, you have two options:
- concatenate these files into just one file
- create for each text file new directory and copy that audio file there to get one text file for one audio file

The audio might be stereo or mono, but tree-2-json.py will create the missing one.
Audio might be stereo or mono, *tree-2-json.py* will create the missing one. All operations with audio files are done with both versions.

The best audio format is `.wav`, but if you provide other supported formats  - `.mp3`, `.m4a`,`.flac`, it will be converted to `.wav`

## Transcription file format
The file can have a header with information about the date, place, speakers, etc. These files will be ignored and will remain in the original file.
Transcribed audio segments have to start with time intervals; supported time intervals are *hh:mm:ss-hh:mm:ss* or *mm:ss-mm:ss*.
After this time interval, the text has to follow. Supported is plain text or interview format. If the difference between start time and end time is 0, it will be printed to stdout, and text won't be sanitized.

Text sanitizer will remove the *#* characters, which are used for filled pauses. All brackets with text inside are removed, too.

### Supported transcription file examples
```
596604/2023/01
18. 2. 2023
R: žena, rok narození 1937
E: Řezáčová, Lucie
Transkriptor: Řezáčová, Lucie
Revizor: Kopecká, Tereza
Rousměrov ZR
Českomoravská nářeční podskupina

00:18–19:50
E: Pamatujete si co se dřív vařilo a peklo?
R: No diš sem bila malá tak jo no. Víc se, nejedlo se tak maso, véc se peklo. Ďelalo se z mouki víc, žejo. Pekáče, tašťički s povidlím. Já nevím co ješťe. Takoví samí, víc mouční jídla jak masití, protože nebilo to maso jako teť.

E: A třeba něco co připravovala vaše maminka a babička?
R: Babičku si nepamatuju uš, sfoju teda. A maminka vařila hodňe, protože teda kdisi bila kuchařkou na faře tak hodňe vařila, no ale takoví normálňí bježní jídla, ňic ne* extra nevivářela jako. 
```
The speaker labels (*E*, *R*) are removed after text sanitization.



# Author
Alexander Rastislav Okrucký
xokruc00@stud.fit.vut.cz
