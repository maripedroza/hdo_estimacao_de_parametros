<h1 align="center"> Estimação de Parâmetros - HDO de Ácido Esteárico </h1>

<p align="center">
 <a href="#descricao">Descrição do Projeto</a> •
 <a href="#objetivo">Objetivo</a> •
 <a href="#comousar">Como usar</a>  • 
 <a href="#teoria">Metodologia</a> •  
 <a href="#referencias">Referências</a>
</p>

<h2 id="descricao"> :bookmark: Descrição do Projeto </h2>

Esse projeto foi desenvolvido para o Trabalho de Conclusão de Curso da graduação em Engenharia Química na Universidade Federal do Rio de Janeiro (UFRJ). 

<h2 id="objetivo"> 🎯 Objetivo </h2>

Tem como objetivo proceder a estimação de parâmetros cinéticos das reações de hidrodesoxigenação (HDO) de ácido esteárico para produção de diesel verde, 
viabilizando a posterior simulação do processo. Esse projeto pode ser facilmente adaptado para estudar outros modelos ou processos semelhantes. 

<h2 id="comousar"> ❓ Como usar </h2>

Todos os algoritmos foram desenvolvidos em linguagem <b>Python</b>. Além de algumas bibliotecas padrões da distribuição <a href="https://www.anaconda.com/products/individual">Ananconda</a>, 
também são utilizados os pacotes <a href="https://pythonhosted.org/pyswarm/">pyswarm</a> e <a href="https://pypi.org/project/numdifftools/">numdifftools</a>, 
que podem ser instalados via script da seguinte maneira: 

```python
import subprocess
subprocess.call(['pip','install','pyswarm'])
subprocess.call(['pip','install','numdifftools'])
```

O projeto é dividido em <b>4 arquivos principais</b>. <br>
<ol>
  <li> O script <i>estimacao_simulacao.py</i> contém toda a metodologia de procedimento de estimação de parâmetros, análise estatística dos parâmetros e simulação do processo.
</li>

  <li> O arquivo <i>dados_exp.xlsx</i>, que deve permanecer dentro da pasta <i>HDO_AE</i>, contém o <i>dataset</i> utilizado 
  para a estimação dos parâmetros a partir do treinamento dos modelos. Os dados experimentais das reação de HDO de ácido esteárico
  foram extraídos dos gráficos de Arora et al. (2019) e organizados em uma planilha Excel. 
  </li>

  <li> O script <i>modelos.py</i>, também localizado no diretório <i>HDO_AE</i>, apresenta toda a modelagem cinética do processo, 
  bem como os códigos referentes à geração dos gráficos de simulação. No contexto do trabalho, 
  foram estudados 5 modelos distintos a serem apresentados mais a frente na seção <a href="#teoria">Fundamentação Teórica</a>. 
  O usuário deve fazer as modificações matemáticas necessárias para avaliar outros modelos ou processos.
  </li>
  
  <li> O script <i>variaveis.py</i>, que assim como os dois arquivos anteriores deve estar na pasta <i>HDO_AE</i>, é onde o usuário define as variáveis do modelo estudado, 
  como as quantidades de experimentos analisados, variáveis independentes, variáveis dependentes e parâmetros a serem estimados.
  </li>
  
</ol>

Durante todo o procedimento de estimação e simulação são gerados tabelas, relatórios e gráficos, que são salvos em pastas específicas para cada modelo, nomeadas <i>Modelo1</i>, <i>Modelo2</i>, e assim por diante.


<h2 id="teoria"> ⚗️ Metodologia </h2>

### Rota Reacional

Na rota reacional proposta neste trabalho para o processo de HDO de ácido esteárico (AE), a formação de hidrocarbonetos de 17 carbonos (C<sub>17</sub>) 
ocorre pela remoção direta de uma molécula de CO<sub>2</sub> através da hidrogenação do reagente. Já a formação de hidrocarbonetos de 18 carbonos (C<sub>18</sub>)
acontece primeiramente pela formação de 1-octadecanal (C<sub>18</sub>=O), seguida da hidrogenação deste a 1-octadecanol (C<sub>18</sub>OH), que por sua vez é hidrogenado
a C<sub>18</sub>, gerando moléculas de água como subproduto.

Reação 1: AE + H<sub>2</sub> → C<sub>17</sub> + CO<sub>2</sub> <br>
Reação 2: AE → C<sub>18</sub>=O - H<sub>2</sub>O <br>
Reação 3: C<sub>18</sub>=O + H<sub>2</sub> → C<sub>18</sub>OH <br>
Reação 4: C<sub>18</sub>OH + H<sub>2</sub> → C<sub>18</sub> - H<sub>2</sub>O <br>

### Modelos Cinéticos Avaliados

Uma vez que o processo estudado se trata de um conjunto de reações heterogêneas, que ocorrem na superfície de catalisadores sólidos, os modelos cinéticos de
Eley-Rideal e de Langmuir-Hinshelwood foram avaliados, considerando diferentes hipóteses para a etapa de adsorção.

<ol>
<li> <b> Modelo ER:</b> </li>
<li> <b> Modelo LH-C-ND:</b> </li>
<li> <b> Modelo LH-C-D:</b>  </li>
<li> <b> Modelo LH-NC-D:</b> </li>
<li> <b> Modelo LH-NC-ND:</b> </li>
</ol>

### Estimação dos parâmetros

O procedimento de estimação de parâmetros procedeu-se de forma a minimizar o função objetivo de mínimos quadrados ponderados, 
que representa a distância entre os dados experimentais e as previsões do modelo.
Para a otimização da função, utilizou-se o método heurístico de Enxame de Partículas definindo uma região de busca, seguido do método de busca direta de Nelder Mead.

<!-- 
<p align="center">
<img src="https://bit.ly/3E3ImSR" align="center" border="0" alt="F_{obj} = \sum_n^{NE}\sum_i^{NY}\:\frac{{ (y^{calc}_{n,i} - y^{exp}_{n,i} ) }^2}{w_{n,i}^2}" width="226" height="62" />
</p>

Em que y<sup>calc</sup> é a variável dependente calculada pelo modelo, y<sup>exp</sup> é o dado experimental, w é o fator de ponderação, 
NE é o número de experimentos e NY é o número de variáveis dependentes.

-->

Para a análise estatística dos parâmetros, utilizou-se o método da Região de Verossimilhança com um nível de confiança de 95%
para construir os intervalos de confiança; a correlação de Pearson para avaliar a predição de cada variável dependente; e a correlação paramétrica
entre cada par de parâmetro.

<h2 id="referencias"> 📜 Referências </h2>

<ul>
<li><a href="https://doi.org/10.1016/j.cej.2019.01.134"> Arora et al. (2019)</a>: artigo de onde os dados experimentais da HDO de ácido esteárico foram extraídos. </li>
<li><a href="https://doi.org/10.1109/ICNN.1995.488968"> Kennedy e Eberhart (1995)</a>: publicação original sobre a otimização por Enxame de Partículas. </li>
<li><a href="https://doi.org/10.1093/comjnl/7.4.308"> Nelder e Mead (1965)</a>: publicação original sobre o algoritmo de Nelder e Mead. </li>
<li> HILL JR, C. G; ROOT, T. W. Chapter 6. Elements of Heterogeneous Catalysis. In: <b>Introduction to Chemical Engineering Kinetics and Reactor Design.</b> 2. ed. 2014. p. 152–188.</li>
<li> SCHWAAB, M.; PINTO, J. C. <b>Análise de Dados Experimentais I</b>, 1. ed. Rio deJaneiro, E-Papers, 2007. </li>
</ul>



