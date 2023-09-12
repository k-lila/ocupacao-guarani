import pandas as pd
import plotly.graph_objs as go
import numpy as np

# ==================================================================================================================== #
class Escavator(object):
    '''
        Uma pequena classe que permite extrair e visualizar os dados do sítio RS-TQ-141.
    '''
    def __init__(self):
        self.dataframe = pd.read_excel('database.xlsx')
        self.filtro = self.dataframe
        self.tracos = None
# --------------------------------------------------- #
    def filtrar(self, quadrante: int, sondagem=None):
        if sondagem:
        # filtra o dataframe segundo o quadrante e a sondagem
            self.filtro = self.dataframe.loc[
                (self.dataframe['Quadrante'] == str(quadrante)) 
                & (self.dataframe['Sondagem'] == str(sondagem)), :
                ]
        else:
        # filtra o dataframe seguindo o quadrante
            self.filtro = self.dataframe.loc[self.dataframe['Quadrante'] == quadrante]
        return self
# --------------------------------------------------------------------------------- #
    def get_trace(self, df=None):
        # seleciona o dataframe
        dataframe = None
        if df is not None:
            dataframe = df
        else:
            dataframe = self.filtro
        # retira os valores nan
        dataframe = dataframe.dropna(subset=['x', 'y', 'z'])
        # separa os dataframes segundo a coluna 'Material'
        carvao = dataframe.loc[dataframe['Material'] == 'Carvão']
        ceramica = dataframe.loc[dataframe['Material'] == 'Cerâmica']
        litico = dataframe.loc[dataframe['Material'] == 'Lítico']
        osso = dataframe.loc[dataframe['Material'] == 'Osso']
        # cria os plots e salva em variáveis
        carvao = go.Scatter3d(
            x=carvao['x'],
            y=carvao['y'], 
            z=carvao['z'],
            mode='markers', 
            marker=dict(size=5, color='black', symbol='square'), 
            text=dataframe["Nº de Registro"],
            name='Carvão' 
        )
        ceramica = go.Scatter3d(
            x=ceramica['x'],
            y=ceramica['y'], 
            z=ceramica['z'], 
            mode='markers', 
            marker=dict(size=5, color='darkcyan', symbol='diamond'), 
            text=dataframe["Nº de Registro"],
            name='Cerâmica' 
        )        
        litico = go.Scatter3d(
            x=litico['x'], 
            y=litico['y'], 
            z=litico['z'], 
            mode='markers', 
            marker=dict(size=5, color='gray', symbol='circle'), 
            text=dataframe["Nº de Registro"],
            name='Lítico' 
        )        
        osso = go.Scatter3d(
            x=osso['x'], 
            y=osso['y'], 
            z=osso['z'], 
            mode='markers', 
            marker=dict(size=5, color='black', symbol='cross'), 
            text=dataframe["Nº de Registro"],
            name='Osso' 
        )
        self.tracos = [carvao, ceramica, litico, osso]
        return self
# -------------------------------------------------- #
    def get_figure(self):
        x_maxmin, y_maxmin, z_maxmin = [], [], []
        data = []
        for traco in self.tracos:
            #  Exclui os traços vazios
            if len(traco['x']) == 0:
                pass
            else:
                data.append(traco)
                x_maxmin.append(np.nanmax(traco['x']))
                x_maxmin.append(np.nanmin(traco['x']))
                y_maxmin.append(np.nanmax(traco['y']))
                y_maxmin.append(np.nanmin(traco['y']))
                z_maxmin.append(np.nanmax(traco['z']))
                z_maxmin.append(np.nanmin(traco['z']))
        # define as variáveis de máximo e mínimo dos eixos
        x_min, x_max = min(x_maxmin), max(x_maxmin)
        y_min, y_max = min(y_maxmin), max(y_maxmin)
        z_min, z_max = min(z_maxmin), max(z_maxmin)
        # define as variáveis que vão ajustar a proporção da figura 
        referencia = z_max - z_min
        dif_x, dif_y = (x_max - x_min) / referencia, (y_max - y_min) / referencia
        # fig     
        fig = go.Figure(data=data)
        # fig layout
        fig.update_layout(scene=dict(
            xaxis=dict(range=[x_min - 10, x_max + 10]),
            yaxis=dict(range=[y_min - 10, y_max + 10]),
            zaxis=dict(range=[z_min - 10, z_max + 10]),
            aspectratio=dict(x=dif_x, y=dif_y, z=1),
            ))
        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            autosize=True
        )
        return fig
# ==================================================================================================================== #
escavacao = Escavator()
# -------------------- #
def update_sitio_json():
    sitio_fig = escavacao.get_trace().get_figure()
    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=2, y=0, z=-1),
        eye=dict(x=10, y=4, z=7)
    )
    sitio_fig.update_layout(scene=dict(camera=camera))
    sitio_json = sitio_fig.to_json()

    with open('sitio.json', mode='w') as json_file:
        json_file.write(sitio_json)
# -------------------------------- #
def update_acampamento():
    acampamento_df = pd.concat([
        escavacao.filtrar(quadrante=1, sondagem=5).filtro,
        escavacao.filtrar(quadrante=1, sondagem=10).filtro,
        escavacao.filtrar(quadrante=1, sondagem=15).filtro,
        escavacao.filtrar(quadrante=2, sondagem=11).filtro,
        escavacao.filtrar(quadrante=2, sondagem=12).filtro,
        escavacao.filtrar(quadrante=2, sondagem=13).filtro,
        escavacao.filtrar(quadrante=2, sondagem=14).filtro,
        escavacao.filtrar(quadrante=2, sondagem=15).filtro
        ], axis=0)
    acampamento_fig = escavacao.get_trace(acampamento_df).get_figure()

    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0.5, y=0, z=-0.3),
        eye=dict(x=3, y=2, z=2)
    )
    acampamento_fig.update_layout(scene=dict(camera=camera))
    acampamento_json = acampamento_fig.to_json()
    with open('acampamento.json', mode='w') as json_file:
        json_file.write(acampamento_json)
# ------------------------------------- #
def update_fogueira_json():
    fogueira_fig = escavacao.filtrar(quadrante=1, sondagem=15).get_trace().get_figure()
    camera = dict(
        up=dict(x=0, y=0, z=1),
        center=dict(x=0, y=0, z=0),
        eye=dict(x=1.5, y=1.5, z=1.5)
    )
    fogueira_fig.update_layout(scene=dict(camera=camera))
    fogueira_json = fogueira_fig.to_json()
    with open('fogueira.json', mode='w') as json_file:
        json_file.write(fogueira_json)
# ------------------------------------- #
def update_plots():
    update_sitio_json()
    update_fogueira_json()
    update_acampamento()
# ==================================================================================================================== #
update_plots()
