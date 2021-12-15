# DEFINICAO DAS VARIAVEIS DO MODELO

NEXP  = 55    #numero de experimentos
NVENT = 9     #numero de variaveis de entrada (independentes)
NVSAI = 5     #numero de variaveis de saida   (dependentes)
NPAR  = 9     #numero de parametros (NPAR = 9 para IMOD == 1 e NPAR = 10 para os demais)
ALPHA = 0.95  #grau de confianca
IMOD  = 1     #indice discrimanatorio do modelo: 
                 # IMOD = 1 para o modelo ER
                 # IMOD = 2 para o modelo LH-C-ND
                 # IMOD = 3 para o modelo LH-C-D
                 # IMOD = 4 para o modelo LH-NC-ND
                 # IMOD = 5 para o modelo LH-NC-D
