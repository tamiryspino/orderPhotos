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


def renameImages(nome, path):
	r=r'^(IMG_|VID_|IMG-|VID-|Screenshot_|InShot_)(\d{8})(.\w*\d*)?([.]\w*\d*)$'
	novo_nome = ""
	success = False
	print(nome)
	if re.search(r,nome):
		if(nome.startswith(("IMG", "VID"))):
			novo_nome = nome[4:]
		elif(nome.startswith("Screenshot_")):
			novo_nome = nome[11:]
		elif(nome.startswith("InShot_")):
			novo_nome = nome[7:]		
		novo_nome = novo_nome[:4] + "-" + novo_nome[4:6] + "-" + novo_nome[6:]
		if os.path.exists(os.path.join(path,novo_nome)):
			print("Arquivo com este nome já existe na pasta. Tentando novamente com + (renomeado em dia atual)")
			novo_nome+=" (renomeado em " + str(datetime.now()) + ")"
		
		print("Rename: " + nome + " to " + novo_nome)
		os.rename(os.path.join(path,nome),os.path.join(path,novo_nome))
		success = True
	return success

def renameAllImages(imagens, path):
	imagens = sorted(os.listdir(path))
	for nome in imagens:
		if renameImages(nome, path):
			renameAllImages(imagens, path)
			break

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
	renameAllImages(arquivosPasta, directory)
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
			#nome = renameImages(nome, directory)
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

f= open("2013.txt","a+")
f.write(diffDates)
f.close() 

#TODO
#1 - Receber pasta como parametro
#2 - Renomear os arquivos DONE
#3 - Agrupar arquivos que possuem mesma data DONE
#4 - Se quantidade de arquivos com mesma data for maior que 4: criar uma pasta para a data DONE
#5 - Colocar os arquivos na pasta DONE
