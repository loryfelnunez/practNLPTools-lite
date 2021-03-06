
# encoding: utf-8
# Practical Natural Language Processing Tools (practNLPTools-lite): Combination of Senna and Stanford dependency Extractor
# Copyright (C) 2014 PractNLP Project
# Original Author: Biplab Ch Das' <bipla12@cse.iitb.ac.in>
# Current Author: Jawahar S <jawahar273@gmail.com>
# URL: <http://www.cse.iitb.ac.in/biplab12>
# URL: http://jawahar273.gitbooks.io (or) http://github.com/jawahar273


"""
A module for interfacing with the SENNA and Stanford Dependency Extractor.
SUPPORTED_OPERATIONS: It provides
Part of Speech Tags,
Semantic Role Labels,
Shallow Parsing (Chunking), 
Named Entity Recognisation (NER),
Dependency Parse and 
Syntactic Constituency Parse. 
Requirement: Java Runtime Environment :)
"""
import subprocess
import os
from platform import architecture, system
class Annotator:
    """
    A general interface of the SENNA/Stanford Dependency Extractor pipeline that supports any of the
    operations specified in SUPPORTED_OPERATIONS.
    
    SUPPORTED_OPERATIONS: It provides Part of Speech Tags, Semantic Role Labels, Shallow Parsing (Chunking), 
    Named Entity Recognisation (NER), Dependency Parse and Syntactic Constituency Parse. 
    Applying multiple operations at once has the speed advantage. For example,
    senna v3.0 will calculate the POS tags in case you are extracting the named
    entities. Applying both of the operations will cost only the time of
    extracting the named entities. Same is true for dependency Parsing.
    SENNA pipeline has a fixed maximum size of the sentences that it can read.
    By default it is 1024 token/sentence. If you have larger sentences, changing
    the MAX_SENTENCE_SIZE value in SENNA_main.c should be considered and your
    system specific binary should be rebuilt. Otherwise this could introduce
    misalignment errors.
    Example:
    """

    def __init__(self, senna_path, dep_path="", dep_model=""):
        self.senna_path = senna_path+os.path.sep
        self.dep_par_path = dep_path
        self.dep_par_model = dep_model
         
        

    def get_cos_name(self, os_name):
        """"
        get the executable binary with respect to the Os name.
        """

        if os_name == 'Linux':
            bits = architecture()[0]
            if bits == '64bit':
                executable='senna-linux64'
            elif bits == '32bit':
                executable='senna-linux32'
            else:
                executable='senna'
        elif os_name == 'Darwin':
            executable='senna-osx'  
        elif os_name == 'Windows':
            executable='senna-win32.exe'
        return self.senna_path+executable

    def getSennaTagBatch(self,sentences):
        input_data=""
        for sentence in sentences:
            input_data+=sentence+"\n"
        input_data=input_data[:-1]
        package_directory = os.path.dirname(self.senna_path)
        os_name = system()
        executable=self.get_cos_name(os_name)
        senna_executable = os.path.join(package_directory,executable)
        cwd=os.getcwd()
        os.chdir(package_directory)
        p = subprocess.Popen(senna_executable,stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        senna_stdout = p.communicate(input=input_data.encode('utf-8'))[0]
        os.chdir(cwd)
        return senna_stdout.decode().split("\n\n")[0:-1]

    def getSennaTag(self,sentence):
        input_data=sentence
        package_directory = os.path.dirname(self.senna_path)
        #print("testing dir",self.dep_par_path, package_directory)
        os_name = system()
        executable=self.get_cos_name(os_name)
        senna_executable = os.path.join(package_directory,executable)
        cwd=os.getcwd()
        os.chdir(package_directory)
        p = subprocess.Popen(senna_executable,stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        senna_stdout = p.communicate(input=input_data.encode('utf-8'))[0]
        os.chdir(cwd)
        return senna_stdout

    def getDependency(self,parse):
        package_directory = os.path.dirname(self.dep_par_path)
        cwd=os.getcwd()
        
        os.chdir(package_directory)
        with open(cwd+"/in.parse","w", encoding='utf-8') as parsefile:
             parsefile.write(parse)
        p=subprocess.Popen(['java','-cp','stanford-parser.jar', 'edu.stanford.nlp.trees.EnglishGrammaticalStructure', '-treeFile', '{}/in.parse'.format(cwd),'-collapsed'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p.wait()    
        stanford_out=p.stdout.read()
        os.chdir(cwd)
        return stanford_out.strip()

    def getAnnotations(self,sentence="", senna_tags=None,dep_parse=False):
        annotations={}
        if not senna_tags:
            senna_tags=self.getSennaTag(sentence).decode()
            senna_tags=[x.strip() for x in senna_tags.split("\n")];senna_tags = senna_tags[0:-2]
        else:
            senna_tags=[x.strip() for x in senna_tags.split("\n")]
        no_verbs=len(senna_tags[0].split("\t"))-6

        words=[];pos=[];chunk=[];ner=[];verb=[];srls=[];syn=[]
        for senna_tag in senna_tags:
            senna_tag=senna_tag.split("\t")
            words+=[senna_tag[0].strip()]
            pos+=[senna_tag[1].strip()]
            chunk+=[senna_tag[2].strip()]
            ner+=[senna_tag[3].strip()]
            verb+=[senna_tag[4].strip()]
            srl=[]
            for i in range(5,5+no_verbs):
                srl+=[senna_tag[i].strip()]
            srls+=[tuple(srl)]
            syn+=[senna_tag[-1]]
        roles=[]
        for j in range(no_verbs):
            role={}
            i=0
            temp=""
            curr_labels=[x[j] for x in srls]
            for curr_label in curr_labels:
                splits=curr_label.split("-")
                if(splits[0]=="S"):
                    if(len(splits)==2):
                            if(splits[1]=="V"):
                                    role[splits[1]]=words[i]
                            else:
                                    if splits[1] in role:
                                            role[splits[1]]+=" "+words[i]
                                    else:
                                            role[splits[1]]=words[i]
                    elif(len(splits)==3):
                            if splits[1]+"-"+splits[2] in role:
                                    role[splits[1]+"-"+splits[2]]+=" "+words[i]
                            else:
                                    role[splits[1]+"-"+splits[2]]=words[i]  
                elif(splits[0]=="B"):
                           temp=temp+" "+words[i]
                elif(splits[0]=="I"):
                    temp=temp+" "+words[i]
                elif(splits[0]=="E"):
                    temp=temp+" "+words[i]
                    if(len(splits)==2):
                            if(splits[1]=="V"):
                                    role[splits[1]]=temp.strip()
                            else:
                                       if splits[1] in role:
                                            role[splits[1]]+=" "+temp
                                            role[splits[1]]=role[splits[1]].strip()
                                       else:
                                            role[splits[1]]=temp.strip()
                    elif(len(splits)==3):
                                 if splits[1]+"-"+splits[2] in role:
                                      role[splits[1]+"-"+splits[2]]+=" "+temp
                                      role[splits[1]+"-"+splits[2]]=role[splits[1]+"-"+splits[2]].strip()
                                 else:
                                    role[splits[1]+"-"+splits[2]]=temp.strip()
                    temp=""          
                i+=1
            if("V" in role):
                roles+=[role]
        annotations['words']=words
        annotations['pos']=list(zip(words,pos))
        annotations['ner']=list(zip(words,ner))
        annotations['srl']=roles
        annotations['verbs']=[x for x in verb if x!="-"]
        annotations['chunk']=list(zip(words,chunk))
        annotations['dep_parse']=""
        annotations['syntax_tree']=""
        for (w,s,p) in zip(words,syn,pos):
            annotations['syntax_tree']+=s.replace("*","("+p+" "+w+")")
        #annotations['syntax_tree']=annotations['syntax_tree'].replace("S1","S")
        if(dep_parse):
            annotations['dep_parse']=self.getDependency(annotations['syntax_tree'])
        return annotations

def test():  
    """
     please replace the dir of 
     :senna_path: path for senna location
     :dep_path: stanford dependency parser location 
     :dep_model: stanford dependency parser model location
     with your directory 
    """
    from utils import skipgrams 
    annotator=Annotator(senna_path="/media/jawahar/jon/ubuntu/senna/", dep_path="/media/jawahar/jon/ubuntu/senna", dep_model="/media/jawahar/jon/ubuntu/senna")
    #print((annotator.getBatchAnnotations(["He killed the man with a knife and murdered him with a dagger.","He is a good boy."],dep_parse=True)))
    sent = "He created the robot and broke it after making it."
    #"""
    print((annotator.getAnnotations(sent,dep_parse=True)['dep_parse']))
    print((annotator.getAnnotations(sent,dep_parse=True)['chunk']))
    print((annotator.getAnnotations(sent,dep_parse=True)['pos']))
    print((annotator.getAnnotations(sent,dep_parse=True)['ner']))
    print((annotator.getAnnotations(sent,dep_parse=True)['srl']))
    print((annotator.getAnnotations(sent,dep_parse=True)['syntax_tree']))
    print((annotator.getAnnotations(sent,dep_parse=True)['words']))
    print( list(skipgrams(sent.split(), n=3, k=2)) )
    #"""

if __name__ == "__main__":
    test()


