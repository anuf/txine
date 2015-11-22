# -*- coding: utf-8 -*-
"""
@author: Adolfo núñez Fernández
Novembro 2015
"""

import sys # para acceder ás excepcións do sistema
import praw
import xml.etree.ElementTree as ET 
from datetime import datetime  
from sklearn.feature_extraction.text import TfidfVectorizer # TfidfVectorizer

def menu():
    print("\nEscolla unha opción:\n\
    [1] Hot\n\
    [2] Top\n\
    [3] New\n\
    [4] Cancelar")

def mainMenu():
    print("\nEscolla unha opción:\n\
    [1] Obtención de datos e gardado a XML\n\
    [2] Lectura de XML e análise Tfidf\n\
    [3] Saír")
    
def data2XML(submissions, fname):
    ''' Convirte as submissions obtidas a un ficheiro XML '''

    startTime = datetime.now()    
    rootNode = ET.Element('Subreddit')
    rootNode.append(ET.Comment('Xerado para TXINE. Novembro 2015'))
    
    
    i = 0
    
    for submission in submissions: # Cada submission é un post
        try:
            i += 1
            print("Engadindo post {0} ao XML\r".format(i),end='')        
            
            '''
            Descomentar só para obter máis comentarios (se existen) sobre o 
            post. Tarda máis: 10 posts ~ 13'30''  
            '''  
            #submission.replace_more_comments(limit=None, threshold=0)
            
            comments = praw.helpers.flatten_tree(submission.comments)
            
            # Gardamos os atributos que nos interesan de cada submission    
            atrSub = {'author':submission.author.name,
                      'date':str(submission.created),                  
                      'date_utc':str(submission.created_utc),
                      'id':str(submission.id),
                      'num_total_comments':str(submission.num_comments), #inclue os eliminados
                      'num_true_comments':str(len(comments)), #so comments e replys existentes
                      'title':submission.title,
                      'type':'post'
                      }
            elementoPost = ET.SubElement(rootNode, 'Post', atrSub)    
            elementoPost.text = str(submission.title)+' : '+str(submission.selftext) # concatenase titulo e texto
                             
            if len(comments) > 0: #se hai comentarios
                elementoComments = ET.SubElement(elementoPost,'Comments')
                for comment in comments: # Percorremos os comentarios (non aparecen os eliminados) 
                    if hasattr(comment,'body') and hasattr(comment,'author') and str(comment.author) != 'None':
                            atrCom = {'author': comment.author.name,
                                      'date':str(comment.created),                  
                                      'date_utc':str(comment.created_utc),
                                      'id':str(comment.id),
                                      'parent_id':str(comment.parent_id),
                                      'type':'comment' if comment.is_root else 'reply'
                                                }
                            elementoComment = ET.SubElement(elementoComments,'Comment',atrCom)
                            elementoComment.text = str(comment.body) 
        except Exception as e:
            print('Exception: {0}'.format(e))    
    r.http.close()
    # Gardado a ficheiro
    with open(fname, 'wb') as f:
        ET.ElementTree(rootNode).write(f, method='xml')

    print('\nTempo de extracción e almacenamento: {0}'.format(datetime.now() - startTime))
    
def getCorpusFromXML(oXML):
    # Lectura do ficheiro xml
    tree = ET.parse(oXML)
    root = tree.getroot()
    
    # Creamos un corpus para analizar con posts e comentarios 
    posts = [x.text for x in root.iter("Post")]
    comentarios = [x.text for x in root.iter("Comment")]
    
    corpus = posts + comentarios
    print('\nCorpus creado con {0} posts e {1} comentarios'.format(len(posts), len(comentarios)))
    return corpus


def vectorizaCorpus(corpus, minDf):
    ''' Vectoriza o corpus introducido filtrando as palabras que aparecen en 
    menos de minDf documentos'''
    try:
        vectorizer = TfidfVectorizer(min_df = minDf, lowercase=True, stop_words='english')
        
        # Definimos unha lista propoia de stopwords
        myStopwords = ['did','didn','does','doesn','don','just','isn', \
        'reddit', 'wasn','www','yeah','yes','like','able','thanks', \
        'know', 'think','ve', 'want','com','https','http',\
        'good', 'really', 'make', 'say', 'going', 'said', 'people','way', \
        'use']
        
        # engadimos as stop_words que queremos ao conxunto xa existente
        vectorizer.stop_words = vectorizer.get_stop_words().union(myStopwords)
        
        # calculamos a matriz de documentos-términos
        docTerms = vectorizer.fit_transform(corpus)
        
        # invertimos o vocabulario creando un diccionario de índices - termos
        invVoc = {v: k for k, v in vectorizer.vocabulary_.items()} 
        
        # buscamos os termos centrais, que son os que a suma acumulada de tf/idf en todos os documentos é maior
        sumaTfidf = docTerms.sum(axis=0).tolist()[0] #calculamos a suma por columnas da matriz de documentos-termos
    
        return  vectorizer, invVoc, sumaTfidf
    except Exception as e:
        print('\nOcorreu un problema: {0}'.format(e))
        sys.exit()
        
def showResults(vectorizer, invVoc, sumaTfidf, numResults):
    # Almacenamos todo nunha lista para poder amosar os resultados ordeados
    listaResultados = []
    for i in range(len(sumaTfidf)):
        listaResultados.append([invVoc[i], sumaTfidf[i], vectorizer.idf_[i]])
    
    def getKey(item):
        ''' Función que devolve o numero de columna polo que imos ordear a lista '''
        return item[1]
    
    listaResultadosOrdenada = sorted(listaResultados, key = getKey, reverse = True)
    print('{:15s} {:>10s} {:>10s}\n{:45s}'.format('Palabra','Suma','Idf','-'*45))
    for i in range(numResults):
        print('{:15s} {:10.2f} {:10.2f}'.format(listaResultadosOrdenada[i][0],
                                     listaResultadosOrdenada[i][1],listaResultadosOrdenada[i][2]))


if __name__ == "__main__":
    ''' Programa principal. Chamada ao menú de opcións '''
    
    mainOption = 0
    while mainOption != 3:
        
        if mainOption == 1:
            
            # Opción inicial para que entre no bucle
            opcion = 0
              
            while opcion != 4:
                if opcion in (1,2,3):
                    user_agent = "windows:com.exemplo.socialnetworkdataextraction:v1.0 (by /u/rebuldeiro)"
                    r = praw.Reddit(user_agent=user_agent)
                    #r.config.store_json_result = True
                    
                    limite = int(input('Límite de peticións (0 para maximo posible):'))
                    numPetic = str(limite)                    
                    if limite  == 0:
                        limite = None
                        numPetic = 'Max'
                    try:
                        subreddit = str(input('Comunidade (subreddit) a analizar: '))
                        comunidade = r.get_subreddit(subreddit, fetch=True)
                    except praw.errors.InvalidSubreddit:
                        print('Non existe a comunidade {0}\n'.format(subreddit))
                        sys.exit()
                        
                if opcion == 1: # HOT
                    print("Obtendo {0} posts {1} de {2}".format(numPetic, 'HOT', comunidade))
                    submissions = comunidade.get_hot(limit=limite) 
                    tipo = 'HOT'
                    print('[FEITO]')
                elif opcion == 2: # TOP
                    print("Obtendo {0} posts {1} de {2}".format(numPetic, 'TOP', comunidade))
                    submissions = comunidade.get_top(limit=limite)
                    tipo = 'TOP'                    
                    print('[FEITO]')
                elif opcion == 3: # NEW
                    print("Obtendo {0} posts {1} de {2}".format(numPetic, 'NEW', comunidade))
                    submissions = comunidade.get_new(limit=limite)
                    tipo = 'NEW'
                    print('[FEITO]')
                else:
                    pass
                # se a opción é unha da que nos interesa
                if opcion in (1,2,3):
                    fname = input('Nome de ficheiro XML a gardar (sen extensión): ')
                    if fname:
                        fname += '.xml'
                    else:
                        fname = '{0}_{1}_{2}.xml'.format(tipo, subreddit, limite)
                    
                    data2XML(submissions, fname)
                    break
                    
                #chamada ao menú
                menu()
                # Recóllese a opción do usuario
                opcion = int(input('Opción: '))
            
            mainOption = 0
        
        elif mainOption == 2:
            try:
                fxml = input('Nome de ficheiro (sen extensión): ') 
                corpus = getCorpusFromXML(fxml+'.xml')
                minDf = 10
                numResults = 10                
                vectorizer, invVoc, sumaTfidf = vectorizaCorpus(corpus, minDf)
                showResults(vectorizer, invVoc, sumaTfidf, numResults)
            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno,'Non se atopou o ficheiro'))
            except:
                print ("Produciuse un erro inesperado:", sys.exc_info()[0])
                raise

            mainOption = 0
        else:
            pass
    
        #chamada ao menú principal
            mainMenu()
            # Recóllese a opción do usuario
            mainOption = int(input('Opción principal: '))        
    if mainOption == 3:
        print("Adeus")