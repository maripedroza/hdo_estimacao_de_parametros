import numpy as np
from scipy.integrate import odeint
from scipy.constants import R as _R
from . import variaveis
from numba import njit
from matplotlib import pyplot as plt
import matplotlib.lines as mlines
from pathlib import Path

NVSAI = variaveis.NVSAI #numero de variaveis de saida
IMOD = variaveis.IMOD   #indice do modelo

# Caminho da pasta onde os graficos de simulacao serao salvos
if   IMOD == 1: 
    SAVE = Path('HDO_AE\Modelo1') 
elif IMOD == 2: 
    SAVE = Path('HDO_AE\Modelo2') 
elif IMOD == 3: 
    SAVE = Path('HDO_AE\Modelo3') 
elif IMOD == 4: 
    SAVE = Path('HDO_AE\Modelo4') 
elif IMOD == 5: 
    SAVE = Path('HDO_AE\Modelo5') 

# Funcao dos balancos de massa do reator batelada para cada modelo
@njit 
def dNi(N,t,k1,k2,k3,k4,Ksa,Kh2,V,w,Ch2,scratch_N,T,P,n_c12,nH2): 

    # Concentracao em mol m-3 com reuso de memoria
    C = scratch_N  
    C[:]  = N/V     
    
    if   IMOD == 1: #MODELO ER
         
        r1 = (k1*C[0]*Ch2)/(1 + Ksa*C[0])  #taxa da reacao 1
        r2 = (k2*C[0])/(1 + Ksa*C[0])      #taxa da reacao 2
        r3 = (k3*C[1]*Ch2)/(1 + Ksa*C[0])  #taxa da reacao 3
        r4 = (k4*C[2]*Ch2)/(1 + Ksa*C[0])  #taxa da reacao 4
    
    elif IMOD == 2: #MODELO LH-C-ND
        
        # Taxas de reacoes
        r1 = (k1*C[0]*Ch2)/(1 + Ksa*C[0] + Kh2*Ch2)**2
        r2 = (k2*C[0])/(1 + Ksa*C[0] + Kh2*Ch2)
        r3 = (k3*C[1]*Ch2)/(1 + Ksa*C[0] + Kh2*Ch2)**2
        r4 = (k4*C[2]*Ch2)/(1 + Ksa*C[0] + Kh2*Ch2)**2

    elif IMOD == 3: #MODELO LH-C-D
    
        # Taxas de reacoes
        r1 = (k1*C[0]*(Ch2)**0.5)/(1 + Ksa*C[0] + (Kh2*Ch2)**0.5)**2
        r2 = (k2*C[0])/(1 + Ksa*C[0] + (Kh2*Ch2)**0.5)
        r3 = (k3*C[1]*(Ch2)**0.5)/(1 + Ksa*C[0] + (Kh2*Ch2)**0.5)**2
        r4 = (k4*C[2]*(Ch2)**0.5)/(1 + Ksa*C[0] + (Kh2*Ch2)**0.5)**2

    elif IMOD == 4: #MODELO LH-NC-ND
        
        # Taxas de reacoes
        r1 = (k1*C[0]*Ch2)/((1 + Ksa*C[0])*(1 + Kh2*Ch2))
        r2 = (k2*C[0])/(1 + Ksa*C[0])
        r3 = (k3*C[1]*Ch2)/((1 + Ksa*C[0])*(1 + Kh2*Ch2))
        r4 = (k4*C[2]*Ch2)/((1 + Ksa*C[0])*(1 + Kh2*Ch2))

    elif IMOD == 5: #MODELO LH-NC-D  
        
        # Taxas de reacoes
        r1 = (k1*C[0]*(Ch2**0.5))/((1 + Ksa*C[0]) * (1 + (Kh2*Ch2)**0.5))
        r2 = (k2*C[0])/((1 + Ksa*C[0]))
        r3 = (k3*C[1]*(Ch2**0.5))/((1 + Ksa*C[0]) * (1 + (Kh2*Ch2)**0.5))
        r4 = (k4*C[2]*(Ch2**0.5))/((1 + Ksa*C[0]) * (1 + (Kh2*Ch2)**0.5))
           
    # Balancos de massa
    vetor_dNi = scratch_N       
    vetor_dNi[0] = (-r1 - r2)*w   #AE
    vetor_dNi[1] = (r1 - r3 )*w   #C18=O   
    vetor_dNi[2] = (r3 - r4)*w    #C18OH
    vetor_dNi[3] = r2*w           #C17
    vetor_dNi[4] = r4*w           #C18
    
    return vetor_dNi

def MODEL(XE , YE, VPAR, simulation = False):
    
    # Variaveis de entrada traduzidas
    t       = XE[:,0]          #tempo em min
    T       = XE[0,1]+273.15   #temperatura em K
    n_c12   = XE[0,2]          #mols de C12 na alimentacao
    n_sa    = XE[0,3]          #mols de AE na alimentacao
    nH2     = XE[0,4]          #mols de H2 na mistura reacional
    V       = XE[0,5]          #volume da mistura em m3 
    P       = XE[0,6]          #pressao em bar
    w       = XE[0,7]          #massa de catalisador em kg       
    wt_sa   = XE[0,8]*100      #porcentagem massica de ac. estearico no inicio da reacao
    
    # Parametros a serem estimados
    A = VPAR[0]     #kref1 [m6 (mol kg min)-1]
    B = VPAR[1]*1e3 #E1 [J mol-1]
    C = VPAR[2]     #kref2 [m3 (kg min)-1]
    D = VPAR[3]*1e3 #E2 [J mol-1] 
    E = VPAR[4]     #kref3 [m6 (mol kg min)-1]
    F = VPAR[5]*1e3 #E3 [J mol-1]
    G = VPAR[6]     #kref5 [m3 (kg*min)-1]
    H = VPAR[7]*1e3 #E5 [J mol-1]
    I = VPAR[8]     #Ksa [m3 mol-1] 
    if IMOD == 1:
        J = 0       
    else:
        J = VPAR[9] #Kh2 [m3 mol-1] 
    
    # Concentracao de hidrogenio
    Ch2 = nH2/V #mol m-3
    
    # Constantes de velocidade e adsorcao
    k1 = A*np.exp(B*(1/573.15 - 1/T)/_R)
    k2 = C*np.exp(D*(1/573.15 - 1/T)/_R)
    k3 = E*np.exp(F*(1/573.15 - 1/T)/_R)
    k4 = G*np.exp(H*(1/573.15 - 1/T)/_R)
    Ksa = I    
    Kh2 = J 
    
    # Vetor das concentracoes iniciais de reagente, intermediarios e produtos
    Ni0 = np.array([ n_sa , 1e-20 , 1e-20 , 0. , 0. ])  
    
    scratch_r = np.zeros((5,))
      
    if simulation == False: #default: apenas calcula as variaveis de saida para o procedimento de estimacao de parametros
        
        # Vetor tempo com inicio em 0 min
        t = np.concatenate([ [0.], t ])
        
        # Calculo da integral das equacoes de balanco molar
        sol = odeint(dNi, Ni0, t, args=(k1,k2,k3,k4,Ksa,Kh2,V,w,Ch2,scratch_r,T,P,n_c12,nH2)) 
        
        YC = np.zeros([len(XE),NVSAI])
        j=0
        for tf in t[1:]:            
            y = sol[j+1,:] 
            
            # Alocacao dos resultados da integral
            YC[j,:] = (y.real)*1e2/(np.sum(y)) 
            
            j+=1
            
        return YC #retorna as variaveis de saida calculadas pelo modelo
    
    elif simulation == True: #gera os graficos de simulacao
               
        vetor_tempos = np.arange(0,t[-1],1)
        
        # Calculo da integral das equacoes de balanco molar
        sol = odeint(dNi, Ni0, vetor_tempos, args=(k1,k2,k3,k4,Ksa,Kh2,V,w,Ch2,scratch_r,T,P,n_c12,nH2)) 
        
        YC = np.zeros([len(vetor_tempos),NVSAI])
        j=0
        for tf in vetor_tempos:            
            y = sol[j,:] 
            
            # Alocacao dos resultados da integral
            YC[j,:] = (y.real)*1e2/(np.sum(y)) 
            
            j+=1
            
        T = T - 273.15 #convertando a temperatura para °C
         
        # Grafico das fracoes molares de reagente e produtos em funcao do tempo
        f=plt.figure(figsize=(6, 5), dpi=150)
        
        plt.tick_params(labelsize=14)
        
        plt.plot( vetor_tempos , YC [ : , 0 ] , label='AE' , color = 'black')    
        plt.plot( t , YE [ : , 0 ] , 'o' , color = 'black' )
        
        plt.plot( vetor_tempos , YC [ : , 3 ] , label='C$_{17}$' , color = 'tab:red' )
        plt.plot( t , YE [ : , 3 ] , 's' , color = 'tab:red' )
        
        plt.plot( vetor_tempos , YC [ : , 4 ] , label='C$_{18}$' , color = 'tab:green' )    
        plt.plot( t , YE [ : , 4 ] , '^' , color = 'tab:green' )
        
        plt.plot( vetor_tempos , YC [ : , 1 ] , label='C$_{18}$=O' , color = 'mediumblue' )    
        plt.plot( t , YE [ : , 1 ] , 'x' , color = 'mediumblue' )
        
        plt.plot( vetor_tempos , YC [ : , 2 ] , label='C$_{18}$OH' , color = 'orange' )    
        plt.plot( t , YE [ : , 2 ] , '*' , color = 'orange' )
        
        a= tf/2-15
        plt.text(a,0.93*100,str(int(T))+' °C', fontsize=13)
        plt.text(a,0.87*100,str(int(P))+' bar', fontsize=13)
        plt.text(a-5.5,0.81*100,str(int(wt_sa))+' wt% SA', fontsize=13)
        
        plt.xlabel('Tempo (min)',fontsize=15)
        plt.ylabel('Composição molar (%)',fontsize=15)
        
        plt.axis([0, t[-1], 0, 100])
        
        mae = mlines.Line2D([], [], color='black', marker='o', linestyle='solid',
                          markersize=7, label='AE')
        mc17 = mlines.Line2D([], [], color='tab:red', marker='s', linestyle='solid',
                         markersize=7, label='C$_{17}$')
        
        mc18 = mlines.Line2D([], [], color='tab:green', marker='^', linestyle='solid',
                          markersize=7, label='C$_{18}$')
        
        mc18oh = mlines.Line2D([], [], color='orange', marker='*', linestyle='solid',
                  markersize=7, label='C$_{18}$OH')
        
        mc18o = mlines.Line2D([], [], color='mediumblue', marker='x', linestyle='solid',
                          markersize=7, label='C$_{18}$=O')
        
        plt.legend(handles=[mae, mc17, mc18, mc18oh, mc18o])
        
        plt.show()
        f.savefig((SAVE/f'Modelo {IMOD} - {int(T)} °C, {int(P)} bar, {int(wt_sa)} wt%.pdf'))

        return