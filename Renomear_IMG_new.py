#Renomeia os arquivos tirando as iniciais "IMG_", "IMG-", "VID-" ou "VID_" e separa ano, mes e dia por hifens.
import os
from datetime import datetime
import re

def groups(regex, s):
	m = re.search(regex,s)
	if m:
		return m.groups()
	return ('',) * num_groups(regex)

def num_groups(regex):
	return re.compile(regex).groups


def rename_image(name, path):
	regex="(^((IMG|VID|Screenshot|InShot|PANO)(_|-))(((\d){4})-?((\d){2})-?((\d){2}).(\w*\d*)?)|(^((\d){4})-?((\d){2})-?((\d){2}).(\w*\d*)?))"
	regex_subs=r"\6\14-\8\16-\10\18_\12\20"
	new_name = re.sub(regex, regex_subs, name)
	if ((name!=new_name) and (os.path.exists(os.path.join(path,new_name)))):
		print("Arquivo com este nome já existe na pasta. Tentando novamente com + (renomeado em dia atual)")
		new_name = re.sub("(.*)(\.\w*)",r"\1 (renomeado em " + str(datetime.now()) + ")"+ r"\2",new_name)
		print("Rename: " + name + " to " + new_name)
	os.rename(os.path.join(path,name),os.path.join(path,new_name))
	return True

def rename_all_images(imagens, path):
	imagens = sorted(os.listdir(path))
	for nome in imagens:
		rename_images(nome, path)

def doDict(imagens):
	dict = {}
	for i in imagens:
		sep = groups(regex,i)
		dict.setdefault(sep[0],[]).append(sep[0]+sep[1])
	if '' in dict:
		del dict['']
	return dict

def printDict(dict):
	count=0
	countFiles=0
	for key in dict.keys():
		values=dict[key]
		if(len(values) > 4):
			print(key, "=>", len(values), "items: ", values)
			count = count+1
			countFiles=countFiles+len(values)
			print("Quantidade de pastas com mais de 4 arquivos: " + str(count))
			print("Quantidade total de arquivos inseridos nas pastas: " + str(countFiles))

def createDirsAndMove(dict, directory):	
	for key in dict.keys():
		newDir = directory+"/"+key+"/"
		if len(dict[key])>4 and not directory.startswith(key):
			if not os.path.exists(newDir):
				os.makedirs(newDir)
				print("New dir:" + newDir)
			for val in dict[key]:
				file = directory+"/"+val
				if (os.path.isfile(file)):
					print("File: " + file + " will be moved to: " + newDir+val)
					os.rename(file, newDir+val)	
			print(str(len(dict[key])) + "files moved")

def doRefactory(arquivosPasta, directory):
	rename_all_images(arquivosPasta, directory)
	arquivosPasta = sorted(os.listdir(directory))
	dict = doDict(arquivosPasta)
	#printDict(dict)
	#createDirsAndMove(dict, directory)
	#if (arquivosPasta) and not os.path.isdir():
	#	print " - - - - - Não movidos - - - - - "
	#	print arquivosPasta
	return arquivosPasta

def dateImages(regex, s):
	m = re.search(regex,s)
	return m

def getDiffDateMod(regex, arquivosPasta, directory):
	diffDates=""	
	arquivosPasta = doRefactory(arquivosPasta, directory)
	for nome in arquivosPasta:
		arquivo = directory+"/"+nome
		if(os.path.isfile(arquivo)):
			#nome = rename_images(nome, directory)
			if(dateImages(regex, nome)):
				dataArquivo = datetime.fromtimestamp(os.path.getmtime(arquivo)).strftime("%Y-%m-%d")
				if (nome[:10] != dataArquivo):
					diffDates += arquivo+ " --> " + nome[:10] + " x " + dataArquivo + "\n"
		elif os.path.isdir(arquivo):
			#print("Pasta:" + arquivo)
			arquivosPastaInterior = sorted(os.listdir(arquivo))
			diffDates += getDiffDateMod(regex, arquivosPastaInterior, arquivo)
	return diffDates


#Comeca com data (%Y-%m-%d), pode ter complemento (ex.: _29382329) e termina com a ext (ex.: .jpg)
regex = r'^(\d{4}-\d{2}-\d{2})(.*?[.]\w*\d*)$'
directory = os.getcwd()
arquivosPasta = sorted(os.listdir('.'))

diffDates = getDiffDateMod(regex, arquivosPasta, directory)

f= open("2018.txt","a+")
f.write(diffDates)
f.close() 

#TODO
#1 - Receber pasta como parametro
#2 - Renomear os arquivos DONE
#3 - Agrupar arquivos que possuem mesma data DONE
#4 - Se quantidade de arquivos com mesma data for maior que 4: criar uma pasta para a data DONE
#5 - Colocar os arquivos na pasta DONE
