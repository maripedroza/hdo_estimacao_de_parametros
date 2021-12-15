### Importar bibliotecas

import numpy as np                     # manipulacao de arrays
import numdifftools as nd              # calculo diferencial           
import pandas as pd                    # dataframes 
from matplotlib import pyplot as plt   # graficos
from scipy import stats                # estatistica
from scipy import optimize as opt      # metodos de otimizacao  
from pyswarm import pso                # metodo do enxame de particulas
from importlib import import_module    # importacao de modulos
from pathlib import Path               # caminhos
import locale                          # localizacao

### Define Brasil como localizacao para trocar '.' por ',' como separador decimal
locale.setlocale(locale.LC_ALL, 'pt_BR')

#%% PARTE I: ESTIMACAO DE PARAMETROS
##
##
#%% Carregar dados experimentais e variaveis

# Caminho da pasta dos modulos 'modelos' e 'variaveis'
CASE = Path('HDO_AE')

# Tabela de dados experimentais
DadosExp = pd.read_excel(CASE/'dados_exp.xlsx') 

# Carregamento das variaveis
var    = import_module(str(CASE)+'.variaveis')
NEXP   = var.NEXP  #numero de experimentos
NVENT  = var.NVENT #numero de variaveis de entrada
NVSAI  = var.NVSAI #numero de variaveis de saida
NPAR   = var.NPAR  #numero de parametros
ALPHA  = var.ALPHA #grau de confianca
IMOD   = var.IMOD  #indice discrimanatorio do modelo

XEXP   = DadosExp.values[:,0:NVENT]                   #variaveis de entrada
YEXP   = DadosExp.values[:,NVENT:NVENT+2*(NVSAI):2]   #Variaveis de saida
WEIGHT = DadosExp.values[:,NVENT+1:NVENT+2*(NVSAI):2] #fator peso

if   IMOD == 1: 
    # Caminho da pasta onde serao salvos os resultados da estimacao do modelo 1
    SAVE = Path('HDO_AE\Modelo1') 
    
elif IMOD == 2: 
    # Caminho da pasta onde serao salvos os resultados da estimacao do modelo 2
    SAVE = Path('HDO_AE\Modelo2') 
    
elif IMOD == 3: 
    # Caminho da pasta onde serao salvos os resultados da estimacao do modelo 3
    SAVE = Path('HDO_AE\Modelo3') 
    
elif IMOD == 4: 
    # Caminho da pasta onde serao salvos os resultados da estimacao do modelo 4
    SAVE = Path('HDO_AE\Modelo4') 
    
elif IMOD == 5: 
    # Caminho da pasta onde serao salvos os resultados da estimacao do modelo 5
    SAVE = Path('HDO_AE\Modelo5') 


#%% Grau de confianca e calculo de z

cALPHA      = 1 - ALPHA 
hcALPHA_inf = cALPHA/2 
hcALPHA_sup = 1 - hcALPHA_inf 
z           = stats.norm.ppf(q=hcALPHA_sup, loc=0, scale=1) 

#%% Funcao objetivo

# Compilar modelo
modelo = import_module(str(CASE)+'.modelos')
MODEL = modelo.MODEL  #alocacao da funcao MODEL do arquivo "modelo"

# Calculo das variaveis de saida
def Y_Calc(PAR, simulation=False):   

    start = 0 #linha de ininial                      
    end   = 1 #linha final
    YCk   = np.zeros([NEXP,NVSAI]) #alocacao das variaveis de saida

    while end < NEXP:

        #se o tempo for menor do que o anterior, muda a sequencia temporal
        if XEXP[end , 0] <= XEXP[end-1 , 0]: 
            
            YCk[start:end,:] = MODEL(XEXP[start:end , :],YEXP[start:end , :],PAR,simulation)

            start = end
            end += 1
            
        else:            
            end += 1
     
    #fora do loop: ultima sequencia temporal
    YCk[start:end,:] = MODEL(XEXP[start:end , :],YEXP[start:end , :],PAR,simulation)
        
    return YCk 

# Calculo da funcao objetivo de minimos quadrados ponderados 
def objF(PAR):
    
    YCk = Y_Calc(PAR)
    F = np.sum(((YCk - YEXP)**2)/WEIGHT)
    
    return F      

#%% Teste da funcao objetivo

# Parametros do artigo de Arora et al. (2019)
PAR = np.array([5.52e-5, 22.3,
	            8.63e-3,  119,
	            2.78e-3,  159,
	            2.70e-2,  117,
	            5.14e-2,  0])

Fobj = objF(PAR)

print('Fobj =',Fobj,'para PAR =',PAR) 

#%% Funcao Tracer para arquivar em relatorio os valores encontrados ao longo das iteracoes

def sci(x): #formatacao para notacao cientifica
    return f'{x:.8e}' #8 casas decimais

content = [] #conteudo do historico do enxame/simplex

g_FOPT = np.array([np.inf]) #memoria do da funcao objetivo otima global
g_XOPT = np.empty(NPAR)     #memoria do conjunto de parametros otimo global
 
def Tracer_objF(PAR): 

    F = objF(PAR)
    
    content.append(sci(F)+'\t'+'\t'.join([sci(PAR[p]) for p in range(NPAR)])+'\n')  #linha a ser escrita no relatorio
    
    if F < run_FOPT[0]: #se F calculada nesta iteracao for menor que a fopt atual da chamada
        
        run_FOPT[0] = F #F sera a novo fopt
        print(F,PAR)    
        
        if F < g_FOPT[0]:         #se tambem for menor que a fopt global atual
            
            g_FOPT[0] = F         #F ser a nova fopt global
            g_XOPT[:] = PAR[:]    #e o conjunto de parametros tambem sera salvo

    return F

#%% Minimizacao global - Enxame de particulas

# Memoria da fopt a cada chamada
run_FOPT = np.array([np.inf]) 

# Definir limites de busca inferior (lb) e superior (ub) para cada parametro 
# Se IMOD == 1, len(lb) == len(ub) == 9. Para os outros modelos, len(lb) == len(ub) == 10

#               kref1  E1   kref2  E2    kref3  E3    kref4    E4    Ksa   Kh2 
lb = np.array([ 1e-5 ,  0 , 5e-3 , 50  , 5e-4 , 100 ,   5e-3 , 80  , 1e-2 ])#,1e-6]) 
ub = np.array([ 1e-4 , 60 , 5e-2 , 200 , 5e-3 , 200 ,  5e-2 , 180 , 1e-1 ])#,  1e-4]) 

NIT = 500  #numero de iteracoes 
NP  = 100  #numero de particulas

# Chamada da minimizacao
xopt1, fopt1 = pso(Tracer_objF, lb, ub, maxiter=NIT, swarmsize=NP) 
print(xopt1, fopt1)

#%% Historico da minimizacao global

fopt1    = g_FOPT[0] #memoria da funcao objetivo otima de todos os enxames
xopt1[:] = g_XOPT[:] #memoria do conjunto de parametros otimos de todos os enxames

print('Fopt do enxame =', fopt1)
print('xopt do enxame =', xopt1)

f = open(SAVE/f'PSO_GLOBAL_MOD_{IMOD}.txt','w') #nome do arquivo 
f.write( 'F'+'\t'+'\t'.join(['PAR('+str(p)+')' for p in range(NPAR)])+'\n') #cabecalho
f.writelines(content) #conteudo
f.close()

content = [] #excluindo o conteudo do enxame para receber o do simplex
run_FOPT = np.array([np.inf]) 

#%% Minimizacao local - Simplex (rodar ate Success = True)

sol = opt.minimize(Tracer_objF, g_XOPT , method="Nelder-Mead") #chamada da minimizacao
print(sol)

#%% Historico do simplex

fopt2 = g_FOPT[0] #Memoria da funcao objetivo otima do simplex
xopt2 = g_XOPT[:] #Memoria do conjunto de parametros otimos do simplex

f = open(SAVE/f'SIMPLEX_MOD_{IMOD}.txt','w') #nome do arquivo 
f.write( 'F'+'\t'+'\t'.join(['PAR('+str(p)+')' for p in range(NPAR)])+'\n') #cabecalho
f.writelines(content) #conteudo
f.close()

content = [] #excluindo o conteudo do simplex

#%% Amostragem numerosa de pontos proximos ao minimo local para construcao da regiao de confianca
### Enxame de particulas novamente

# Definir limites de busca inferior (lb) e superior (ub) para cada parametro 
# Usar valores PROXIMOS aos valores de xopt2
# Se IMOD == 1, len(lb) == len(ub) == 9. Para os outros modelos, len(lb) == len(ub) == 10

#               kref1   E1   kref2   E2   kref3   E3    kref4   E4    Ksa   Kh2           
lb = np.array([  7e-5 , 5 , 7e-3 ,  30 , 5e-3  , 20  , 8e-5 ,  50 , 4e-2 ])#, 1e-3 ])
ub = np.array([  3e-4 , 70, 3e-2 , 150 , 1e-2  , 250 , 4e-4 , 250 , 9e-2 ])#, 5e-3 ])  

NIT  = 300  #numero de iteracoes 
NP   = 50   #numero de particulas
NRUN = 5    #numero de execucoes do enxame

for i in range(NRUN):
    run_FOPT = np.array([np.inf]) #memoria do fopt a cada enxame
    x_sample, f_sample = pso(Tracer_objF, lb, ub, maxiter=NIT, swarmsize=NP) #chamada da minimizacao
    print(x_sample, f_sample)

#%% Historico da amostragem

f = open(SAVE/f'PSO_SAMPLE_MOD_{IMOD}.txt','w') #nome do arquivo 
f.write( 'F'+'\t'+'\t'.join(['PAR('+str(p)+')' for p in range(NPAR)])+'\n') #cabecalho
f.writelines(content) #conteudo
f.close()

content = [] #excluindo o conteudo da amostragem
run_FOPT = np.array([np.inf]) 

#%% Intervalo de confianca de Fisher - Regiao de Verossimilhanca

GL_Fisher = (NPAR, NEXP*NVSAI-NPAR) #graus de liberdade de FIsher
Flim = fopt2*(1+(GL_Fisher[0]/GL_Fisher[1])*stats.f.ppf(ALPHA,*GL_Fisher)) #F de Fisher

print('fopt do enxame  = ', fopt1)
print('fopt do simplex = ', fopt2)
print('Flim = ', Flim)

#Loop de filtragem da amostragem
def FILTRA_FISHER(Flim):
    
    f2 = open(SAVE/f'PSO_FISHER_MOD_{IMOD}.txt','w') #relatorio

    f2.write( 'F'+'\t'+'\t'.join(['PAR('+str(p)+')' for p in range(NPAR)])+'\n') #cabecalho
    
    
    fTABELA_PSO_ALL = open(SAVE/f'PSO_SAMPLE_MOD_{IMOD}.txt','r')
    fTABELA_PSO_ALL.readline()
    nTUDO = 0
    good  = []
    for linei in fTABELA_PSO_ALL:
        nTUDO += 1
        fields = linei.split('\t')
        f = float(fields[0])
        xopti = [float(fields[pp+1]) for pp in range(NPAR)] 

        if f < Flim:
            good += [ [ f ]+xopti ] 
            f2.write( sci(f)+'\t'+'\t'.join([sci(xopti[p]) for p in range(NPAR)])+'\n') 

    Fgood = np.array(good)
    nGood = np.size(Fgood,axis=0)
    
    f2.close()
    return Fgood,nGood,nTUDO

Fgood,nGood,nTUDO = FILTRA_FISHER(Flim)
print(f'Apos a filtragem, foram aceitas {nGood} de {nTUDO} amostragens.') 

labelsP = [f'PAR({p})'for p in range(NPAR)]

#%% Definicao do intervalo de confianca de cada parametro

def IC_FISHER(F,xopt):
    
    xoptmin = np.array([np.min(F[:,1+i]) for i in range(NPAR)])  #valor minimo de cada parametro
    xoptmax = np.array([np.max(F[:,1+i]) for i in range(NPAR)])  #valor maximo de cada parametro
    xoptave = np.array([np.average([xoptmin[i],xoptmax[i]]) for i in range(NPAR)]) #valor medio de cada parametro
    xoptinc = np.array([xoptave[i] - xoptmin[i] for i in range(NPAR)]) #variacao de cada parametro
    
    
    PARAM = pd.DataFrame(data= np.array([ [round((xoptmin[pp]),6),
                                           round((xopt[pp]),6),
                                           round((xoptmax[pp]),6),
                                           str(round((xoptave[pp]),6))+' +- '+str(round((xoptinc[pp]),6))]
                                       for pp in range(NPAR)]),
                        columns=[r"minimo",r"otimo",r"maximo",r"intervalo"],
                        index=labelsP)
    
    PARAM.to_excel(SAVE/f'regiao_confianca_MOD_{IMOD}.xlsx',sheet_name='Intervalos de confiança')

    return PARAM

PARAM = IC_FISHER(Fgood,xopt2)
print('Intervalos de confianca: \n')
print(PARAM)
print('\nPlanilha salva na pasta.')

#%% PARTE II: AVALIACAO DOS PARAMETROS ESTIMADOS
##
##
#%% Correlaco calculado x experimental

def CORREL(PAR):
    
    # Legendas dos graficos
    Y = ['AE','C$_{18}$=O','C$_{18}$OH', 'C$_{17}$' , 'C$_{18}$']
    a=0

    # Variaveis dependentes calculadas
    YC    = Y_Calc(PAR)
    
    for yy in range(NVSAI):
    
        NUM  = 0. #alocacao do numerador
        DEN1 = 0. #alocacao do termo 1 do denominador
        DEN2 = 0. #alocacao do termo 2 do denominador

        Y_EXP_AVE = np.average(YEXP[:,yy]) #media do valor de de yi experimental 
        Y_CALC_AVE = np.average(YC[:,yy])  #media do valor de yi calculado pelo modelo
    
        for i in range(NEXP):
            NUM  += (YEXP[i,yy]-Y_EXP_AVE)*(YC[i,yy]-Y_CALC_AVE) #calculo do numerador
            DEN1 += (YEXP[i,yy]-Y_EXP_AVE)**2 #calculo do termo 1 do denominador
            DEN2 += (YC[i,yy]-Y_CALC_AVE)**2  #calculo do termo 2 do denominador
    
        CORREL = NUM/np.sqrt(DEN1*DEN2) #calculo do coeficiente de correlacao
        print(CORREL)
        
        # Construcao do grafico Ycalc vs Yexp
        MIN=min(np.nanmin(YEXP[:,yy]),np.nanmin(YC[:,yy]))
        MAX=max(np.nanmax(YEXP[:,yy]),np.nanmax(YC[:,yy]))
        RAN=MAX-MIN    
        lim= MIN-RAN/10, MAX+RAN/10
        
        plt.figure(f'CORRREL{yy}')
        plt.scatter(YEXP[:,yy],YC[:,yy],c='indianred')
        plt.xlim(*lim)
        plt.ylim(*lim)        
        plt.tick_params(labelsize=15)
        plt.ticklabel_format(useLocale='True')
        plt.plot([*lim],[*lim],c='k',ls=':')    
        plt.ylabel(Y[a]+" calculado",fontsize=17)
        plt.xlabel(Y[a]+" experimental",fontsize=17)        
        plt.text(0,0.95*MAX,r'$\rho^m = $'+str(round(CORREL,2)).replace('.',','), fontsize=15)
        plt.savefig((SAVE/f'correl_{yy}_MOD_{IMOD}.pdf'),bbox_inches="tight",pad_inches=0.15)
        plt.show()
        plt.close()
        a+=1
    return

CORREL(xopt2)

#%% Matriz de correlacao parametrica

# Calculo da matriz de covariancia pela aproximacao de Gauss
def f_cova(par0):

    YC  = Y_Calc(par0)
    
    nexp,nvsai = YC.shape
    npar = len(par0)
    
    DFP = np.zeros([NEXP,NVSAI, NPAR])    
    
    def Lmodel(par): 
        YC = Y_Calc(par)
        return YC.reshape([nexp*nvsai])
    
    Lmygrad = nd.Gradient(Lmodel,method='forward') #vetor gradiente
    mygrad  = Lmygrad(par0) 
    DFP[:,:,:] = mygrad.reshape([nexp,nvsai,npar]) #matriz de sensibilidade       
    
    T = np.zeros([NPAR,NPAR]) 
    for k in range(NEXP):
        T += DFP[k,:,:].T @ ( np.diag(1/WEIGHT[k,:]) @ DFP[k,:,:]) 
    
    cova = np.linalg.inv(T) #matriz de covariancia
       
    return cova

cova = f_cova(xopt2)

#%% Matriz de correlacao parametrica

COR = np.zeros([NPAR,NPAR])
for i in range(NPAR):
    for j in range(NPAR):
        COR[i,j] = cova[i,j]/np.sqrt(cova[i,i]*cova[j,j])
        
#%% PARTE III: SIMULACAO DO PROCESSO
##
##
#%% Tabela de comparacao entre os valores calculados pelo modelo e os dados experimentais

YC = Y_Calc(xopt2)

# Calculo do erro relativo de predicao
Y_error = np.zeros((NEXP,NVSAI))
for l in range(NEXP):
    for c in range(NVSAI):
        YC[l,c] = round(YC[l,c],2) #arredondar com duas casas decimais
        YEXP[l,c] = round(YEXP[l,c],2) #arredondar com duas casas decimais
        Y_error[l,c] = (YC[l,c] - YEXP[l,c])*100/YEXP[l,c]
        Y_error[l,c] = round(Y_error[l,c],2) #arredondar com duas casas decimais

# Tabela de resultados        
labelsP = [XEXP[p,0] for p in range(NEXP)]
RESULT = pd.DataFrame(data= np.array([ [YC[pp,0], YEXP[pp,0], str(Y_error[pp,0])+' %',
                                        YC[pp,1], YEXP[pp,1], str(Y_error[pp,1])+' %',
                                        YC[pp,2], YEXP[pp,2], str(Y_error[pp,2])+' %',
                                        YC[pp,3], YEXP[pp,3], str(Y_error[pp,3])+' %',
                                        YC[pp,4], YEXP[pp,4], str(Y_error[pp,4])+' %']
                                       for pp in range(NEXP)]),
                       columns=[r"AE (sim)",r"AE (exp)",r"AE (erro rel)",
                                r"C18=O (sim)",r"C18=O (exp)",r"C18=O (erro rel)",
                                r"C18OH (sim)",r"C18OH (exp)",r"C18OH (erro rel)",
                                r"C17 (sim)",r"C17 (exp)",r"C17 (erro rel)",
                                r"C18 (sim)",r"C18 (exp)",r"C18 (erro rel)"],
                       index=labelsP)

# Criando um arquivo excel (.xlsx) com os resultados
RESULT.to_excel(SAVE/f'tabela_simulacao_MOD_{IMOD}.xlsx',sheet_name=f'Simulado vs Experimental {IMOD}')

#%% Graficos de simulacao

#passa o argumento simulation=True para a funcao MODEL do arquivo 'modelo'
Y_Calc(xopt2,simulation=True) 

print(f'Os gráficos foram salvos na pasta na pasta Modelo{IMOD}.')