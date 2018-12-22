#Renomeia os arquivos tirando as iniciais "IMG_", "IMG-", "VID-" ou "VID_" e separa ano, mes e dia por hifens.
import os

def groups(regex, s):
	import re
	m = re.search(regex,s)
	if m:
		return m.groups()
	return ('',) * num_groups(regex)

def num_groups(regex):
	import  re
	return re.compile(regex).groups


def renameImages(nome, path):
	r=r'^(IMG_|VID_|IMG-|VID-|Screenshot_|InShot_)(\d{8})(.\w*\d*)?([.]\w*\d*)$'
	import re, os
	novo_nome = ""
	if re.search(r,nome):
		if(nome.startswith(("IMG", "VID"))):
			novo_nome = nome[4:]
		elif(nome.startswith("Screenshot_")):
			novo_nome = nome[11:]
		elif(nome.startswith("InShot_")):
			novo_nome = nome[7:]		
		novo_nome = novo_nome[:4] + "-" + novo_nome[4:6] + "-" + novo_nome[6:]
		print "Rename: " + nome + " to " + novo_nome
		os.rename(os.path.join(path,nome),os.path.join(path,novo_nome))
	return novo_nome

def renameAllImages(imagens, path):
	for nome in imagens:
		renameImages(nome, path)

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
			print key, "=>", len(values), "items: ", values
			count = count+1
			countFiles=countFiles+len(values)
			print "Quantidade de pastas com mais de 4 arquivos: " + str(count)
			print "Quantidade total de arquivos inseridos nas pastas: " + str(countFiles)

def createDirsAndMove(dict, directory):	
	for key in dict.keys():
		newDir = directory+"/"+key+"/"
		if len(dict[key])>4 and not directory.endswith(key):
			if not os.path.exists(newDir):
				os.makedirs(newDir)
				print "New dir:" + newDir
			for val in dict[key]:
				file = directory+"/"+val
				if (os.path.isfile(file)):
					print "File: " + file + " will be moved to: " + newDir+val
					os.rename(file, newDir+val)	
			print str(len(dict[key])) + "files moved"

def doRefactory(arquivosPasta, directory):
	renameAllImages(arquivosPasta, directory)
	arquivosPasta = sorted(os.listdir(directory))
	dict = doDict(arquivosPasta)
	printDict(dict)
	createDirsAndMove(dict, directory)
	#if (arquivosPasta) and not os.path.isdir():
	#	print " - - - - - Não movidos - - - - - "
	#	print arquivosPasta
	return arquivosPasta

def dateImages(regex, s):
	import re
	m = re.search(regex,s)
	return m

def getDiffDateMod(regex, arquivosPasta, directory):
	arquivosPasta = doRefactory(arquivosPasta, directory)
	for nome in arquivosPasta:
		arquivo = directory+"/"+nome
		if(os.path.isfile(arquivo)):
			#nome = renameImages(nome, directory)
			if(dateImages(regex, nome)):
				import datetime
				dataArquivo = datetime.datetime.fromtimestamp(os.path.getmtime(arquivo)).strftime("%Y-%m-%d")
				if (nome[:10] != dataArquivo):
					print(arquivo+ " --> " + nome[:10] + " x " + dataArquivo)
		elif os.path.isdir(arquivo):
			print arquivo
			arquivosPastaInterior = sorted(os.listdir(arquivo))
			getDiffDateMod(regex, arquivosPastaInterior, arquivo)


#Comeca com data (%Y-%m-%d), pode ter complemento (ex.: _29382329) e termina com a ext (ex.: .jpg)
regex = r'^(\d{4}-\d{2}-\d{2})(.*?[.]\w*\d*)$'
directory = os.getcwd()
arquivosPasta = sorted(os.listdir('.'))



getDiffDateMod(regex, arquivosPasta, directory)

#TODO
#1 - Receber pasta como parametro
#2 - Renomear os arquivos DONE
#3 - Agrupar arquivos que possuem mesma data DONE
#4 - Se quantidade de arquivos com mesma data for maior que 4: criar uma pasta para a data DONE
#5 - Colocar os arquivos na pasta DONE

