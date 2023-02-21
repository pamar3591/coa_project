# splits the data in /us_text_20200604/data/data.jsonl into year-wise JSON files. The original data is available on file with Nina Varsava. 
# separate json file for each year in directory /us_text_20200604/data/Data/yearData
import os
import json
import sys

def splitIntoYears(dataJsonName,outFolder,outFileNameBase,procYears=None):

	with open(dataJsonName,encoding='UTF-8') as jsonFile:

		for line in jsonFile:
			dataJson = json.loads(line)

			lineYear = dataJson['decision_date'].split('-')[0]

			if procYears == None or lineYear in procYears:

				outFileName = os.path.join(outFolder,str(lineYear)+outFileNameBase)
				with open(outFileName, 'a') as outFile:
					json.dump(dataJson, outFile, ensure_ascii=False)
					outFile.write('\n')


if __name__ == "__main__":

	print("Creating year-wise JSON files for analysis")

	working_dir = os.path.join(sys.argv[1],'raw-caselaw')
	outDir = os.path.join(sys.argv[1])
	dataJsonName = os.path.join(working_dir, "f-appx_text_20200604/data", 'data.jsonl')   # Here we are importing the data.
	outFolder = os.path.join(outDir, 'output_dir', 'Data', 'yearData')

	outFileNameBase = 'fedReporter.json'
	procYears = [str(y) for y in range(2001,2019)]
	splitIntoYears(dataJsonName,outFolder,outFileNameBase,procYears=procYears)

	dataJsonName = os.path.join(working_dir, "f3d_text_20200604/data", 'data.jsonl')
	outFileNameBase = 'appendix.json'
	splitIntoYears(dataJsonName,outFolder,outFileNameBase,procYears=procYears)
