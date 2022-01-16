import sys
from os import listdir
import os
import cv2
import numpy
from PIL import Image
import pytesseract
import pdf2image
import PyPDF2
from pytesseract import Output
import camelot
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

source = 'C:/Users/JUNAID/PycharmProjects/ocr_trial/_splitted/'
if not os.path.exists(source):
    os.mkdir(source)
split_pdfs = os.listdir(source)
for file in split_pdfs:
    os.remove(source + file)
destination_jpg = 'C:/Users/JUNAID/PycharmProjects/ocr_trial/pdf2jpg/'
if not os.path.exists(destination_jpg):
    os.mkdir(destination_jpg)
split_jpg = os.listdir(destination_jpg)
for file in split_jpg:
    os.remove(destination_jpg + file)
save_text_path = 'C:/Users/JUNAID/PycharmProjects/ocr_trial/ocr_textfiles/'
if not os.path.exists(save_text_path):
    os.mkdir(save_text_path)
split_text = os.listdir(save_text_path)
for file in split_text:
    os.remove(save_text_path + file)
final_results = 'C:/Users/JUNAID/PycharmProjects/ocr_trial/FINAL_RESULTS/'
if not os.path.exists(final_results):
    os.mkdir(final_results)
final_result = os.listdir(final_results)
for file in final_result:
    os.remove(final_results + file)
pytesseract.pytesseract.tesseract_cmd = 'C:/Users/JUNAID/AppData/Local/Programs/Tesseract-OCR/tesseract.exe'

Tk().withdraw()
pdf = askopenfilename()
if pdf:
    print("PDF selected: " + pdf)

else:
    print("PDF not selected")
    sys.exit()


def split_pdf(in_pdf, step=1):
    print("Processing.. Please wait ")
    try:
        with open(in_pdf, 'rb') as in_file:
            input_pdf = PyPDF2.PdfFileReader(in_file)
            num_pages = input_pdf.numPages
            input_dir, filename = os.path.split(in_pdf)
            filename = os.path.splitext(filename)[0]
            output_dir = '_splitted/'
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            intervals = range(0, num_pages, step)
            intervals = dict(enumerate(intervals, 1))
            naming = f'{filename}_p'

            count = 0
            for key, val in intervals.items():
                output_pdf = PyPDF2.PdfFileWriter()
                if key == len(intervals):
                    for i in range(val, num_pages):
                        output_pdf.addPage(input_pdf.getPage(i))
                    nums = f'{val + 1}' if step == 1 else f'{val + 1}-{val + step}'
                    with open(f'{output_dir}{naming}{nums}.pdf', 'wb') as outfile:
                        output_pdf.write(outfile)

                    count += 1
                else:
                    for i in range(val, intervals[key + 1]):
                        output_pdf.addPage(input_pdf.getPage(i))
                    nums = f'{val + 1}' if step == 1 else f'{val + 1}-{val + step}'
                    with open(f'{output_dir}{naming}{nums}.pdf', 'wb') as outfile:
                        output_pdf.write(outfile)

                    count += 1
    except FileNotFoundError as err:
        print('Cannot find the specified file. Check your input:')
    print(f'{count} pdf files written to {output_dir}')


def junkjpgs(path):
    pics = os.listdir(path)
    if len(pics) == 0:
        return
    for file in pics:
        os.remove(path + file)


# crack the PDF open

def splitPDF(aPDF, source, destination):
    outputName = aPDF.split('.')
    savename = outputName[0]
    images = pdf2image.convert_from_path(source + aPDF, 500, poppler_path=r'C:\Program Files\poppler-0.68.0\bin')
    i = 1
    for image in images:
        img = cv2.cvtColor(numpy.asarray(image), cv2.COLOR_BGR2GRAY)
        img = cv2.medianBlur(img, 5)
        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        imgg = Image.fromarray(img.astype('uint8'))
        imgg.save(destination + savename + str(i) + '.jpg', 'JPEG')
        i += 1

    savetextname = savename + '.txt'
    return savetextname


def convert2text(name):
    # get the jpgs
    jpgFiles = os.listdir(destination_jpg)
    jpgFiles.sort()
    this_text = open(save_text_path + name, 'w')
    # this works fine
    for i in range(len(jpgFiles)):
        custom_config = r'-c preserve_interword_spaces=1 --oem 1 --psm 1 -l eng'
        d = pytesseract.image_to_data(Image.open(destination_jpg + jpgFiles[i]), config=custom_config,
                                      output_type=Output.DICT)
        df = pd.DataFrame(d)
        # clean up blanks
        df1 = df[(df.conf != '-1') & (df.text != ' ') & (df.text != '')]
        # sort blocks vertically
        sorted_blocks = df1.groupby('block_num').first().sort_values('top').index.tolist()
        for block in sorted_blocks:
            curr = df1[df1['block_num'] == block]
            sel = curr[curr.text.str.len() > 3]
            char_w = (sel.width / sel.text.str.len()).mean()
            prev_par, prev_line, prev_left = 0, 0, 0
            text = ''
            for ix, ln in curr.iterrows():
                # add new line when necessary
                if prev_par != ln['par_num']:
                    text += '\n'
                    prev_par = ln['par_num']
                    prev_line = ln['line_num']
                    prev_left = 0
                elif prev_line != ln['line_num']:
                    text += '\n'
                    prev_line = ln['line_num']
                    prev_left = 0

                added = 0  # num of spaces that should be added
                if ln['left'] / char_w > prev_left + 1:
                    added = int((ln['left']) / char_w) - prev_left
                    text += ' ' * added
                text += ln['text'] + ' '
                prev_left += len(ln['text']) + added + 1
            text += '\n'
            this_text.write(text)
        this_text.close()
    junkjpgs(destination_jpg)


# def find_keyword():
#     Keyword = ['Minimum Eligibility Requirements', 'Deadline for Submission of bids',
#                'Eligibility criteria for sole applicant', 'The time and date of submission']
#     with open(r"C:\Users\JUNAID\PycharmProjects\ocr_trial\found_keyword.txt", "w") as f:
#         for filename in listdir(save_text_path):
#             with open(save_text_path + filename) as currentFile:
#                 text = currentFile.read()
#                 for x in Keyword:
#                     if x in text:
#                         print('Found ' + x + ' in ' + filename[:-4])
#                         f.write('Found ' + x + ' in ' + filename[:-4] + '\n')
#                         # pdf_name = filename.replace('.txt', '.pdf')
#                         # pdf_dir = source + pdf_name
#                         # files = [pdf_dir]
#                         # for file in files:
#                         # tables = camelot.read_pdf(file, pages="1-end")
#                         # tables.export(final_results + "/" + x + ".xlsx", f="excel")
#                         found_keyword = False
#                         with open(save_text_path + filename, 'r') as fd:
#                             for line in fd:
#                                 if x in line:
#                                     found_keyword = True
#                                     if found_keyword:
#                                         with open(final_results + x + ".txt", 'w') as fa:
#                                             print(line)
#                                             fa.writelines(line)
#                                             xx = ['The time and date of submission', 'Deadline for Submission of bids']
#                                             if x in xx:
#                                                 break
#                                             else:
#                                                 for lines in fd:
#                                                     print(lines)
#                                                     fa.writelines(lines)
#                                         fa.close()


if __name__ == '__main__':

    split_pdf(in_pdf=pdf)

    junkjpgs(destination_jpg)

    files = os.listdir(source)
    mypdfs = []

    for f in files:
        if f.endswith('.pdf'):
            mypdfs.append(f)

    for f in mypdfs:
        text_name = splitPDF(f, source, destination_jpg)
        convert2text(text_name)

    find_keyword()
    print("Finished Processing")
