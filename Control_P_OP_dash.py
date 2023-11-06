import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import dash_table
import dash_html_components as html
import dash_core_components as dcc

from dash import dash_table, html, dcc


# Cargamos los datos
data = pd.read_excel("192_Taller.xlsx")

# Inicializamos la aplicación
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Tablero de Control de Operarios'),
    dcc.Dropdown(
        id='mes-dropdown',
        options=[{'label': mes, 'value': mes} for mes in data['Mes'].unique()],
        value='enero'
    ),
       
    dcc.Graph(id='graph'),

   dash_table.DataTable(
    id='table',
    columns=[
        {'name': 'Operario', 'id': 'Nom Ope'},
        {'name': 'Tiempo Invertido', 'id': 'Tiem Inv'},
        {'name': 'Tiempo Facturado', 'id': 'Tiem.fac'},
        {'name': 'Productividad (%)', 'id': 'Productividad'} 
    ],
    style_cell_conditional=[
        {'if': {'column_id': 'Nom Ope'}, 'width': '80px'},
        {'if': {'column_id': 'Tiem Inv'}, 'width': '80px'},
        {'if': {'column_id': 'Tiem.fac'}, 'width': '80px'},
        {'if': {'column_id': 'Productividad'}, 'width': '80px'}
    ],
    style_cell={
        'textOverflow': 'ellipsis',
        'overflow': 'hidden'
    }
),  
    
    html.H2('Detalle por Operario'),
        
        dcc.Dropdown(
        
        id='operario-dropdown',
        options=[{'label': operario, 'value': operario} for operario in data['Nom Ope'].dropna().unique()],
        value=data['Nom Ope'].dropna().unique()[0]
        ),
        html.Div(style={'display': 'flex'}, children=[
        dash_table.DataTable(id='operario-table',
                         style_table={'width': '100%','display': 'inline-block', 'box-sizing': 'border-box'}),
        dcc.Graph(id='operario-graph',
               style={'width': '75%', 'display': 'inline-block', 'box-sizing': 'border-box'})
        ])
         
])

@app.callback(
    [Output('graph', 'figure'), Output('table', 'data')],
    [Input('mes-dropdown', 'value')]
)
def update_graph(selected_mes):
    filtered_data = data[data['Mes'] == selected_mes]

    grouped_data = filtered_data.groupby('Nom Ope').agg({
        'Tiem Inv': 'sum',
        'Tiem.fac': 'sum'
    }).reset_index()

    #Calcula la columna de productividad:
    grouped_data['Productividad'] = (grouped_data['Tiem.fac'] / grouped_data['Tiem Inv']) * 100

    #Calcula la columna de productividad:
    grouped_data['Productividad'] = grouped_data['Productividad'].round(2)

    # Redondeo de valores a 2 decimales
    grouped_data['Tiem Inv'] = grouped_data['Tiem Inv'].round(2)
    grouped_data['Tiem.fac'] = grouped_data['Tiem.fac'].round(2)

    # Barras para "Tiempo Invertido"
    trace1 = go.Bar(
        x=grouped_data['Nom Ope'],
        y=grouped_data['Tiem Inv'],
        name='Tiempo Invertido',
        marker=dict(
            color='#3498DB',           # Color de la barra
                line=dict(color='black', width=1.1)   # Borde de la barra
            )
        )

# Barras para "Tiempo Facturado"
    trace2 = go.Bar(
        x=grouped_data['Nom Ope'],
        y=grouped_data['Tiem.fac'],
        name='Tiempo Facturado',
        marker=dict(
            color='#6C3483',        # Color de la barra
            line=dict(color='black', width=1.1)   # Borde de la barra
            )
        )


    table_data = grouped_data.to_dict('records')

    return {
        'data': [trace1, trace2],
        'layout': go.Layout(
            title='Comparativa Tiempo Invertido vs Tiempo Facturado por Operario',
            xaxis=dict(title='Operario'),
            yaxis=dict(title='Horas'),
            barmode='group',
            plot_bgcolor='#d3d3d3', # Aquí es donde se establece el color de fondo
            paper_bgcolor='#D1F2EB'  # color de fondo del área del papel
            
        )
    }, table_data
@app.callback(
    [Output('operario-table', 'data'), Output('operario-graph', 'figure')],
    [Input('operario-dropdown', 'value')]
)
def update_operario_info(selected_operario):
    filtered_data = data[data['Nom Ope'] == selected_operario]
    grouped_data = filtered_data.groupby('Mes').agg({
        'Tiem Inv': 'sum',
        'Tiem.fac': 'sum'
    }).reset_index()

    #Calcula la columna de productividad:
    grouped_data['Productividad'] = (grouped_data['Tiem.fac'] / grouped_data['Tiem Inv']) * 100

    #Calcula la columna de productividad:
    grouped_data['Productividad'] = grouped_data['Productividad'].round(2)

    # Redondeo de valores a 2 decimales
    grouped_data['Tiem Inv'] = grouped_data['Tiem Inv'].round(2)
    grouped_data['Tiem.fac'] = grouped_data['Tiem.fac'].round(2)

      # Ordenar por mes la tabla 
    months_order = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    grouped_data['Mes'] = pd.Categorical(grouped_data['Mes'], categories=months_order, ordered=True)
    grouped_data = grouped_data.sort_values('Mes')
 
    # Agregar fila total
    total_inv = grouped_data['Tiem Inv'].sum().round(2)#Total con dos decimales
    total_fac = grouped_data['Tiem.fac'].sum().round(2)
    grouped_data = grouped_data.append({
        'Mes': 'Total de Tiempos',
        'Tiem Inv': total_inv,
        'Tiem.fac': total_fac
    }, ignore_index=True)

    # Agregar fila de productividad
    productivity = (total_fac / total_inv) * 100 if total_inv != 0 else 0
    grouped_data = grouped_data.append({
        'Mes': '(X̅ ) de Productividad',
        'Tiem Inv': '',
        'Tiem.fac': round(productivity, 2)
    }, ignore_index=True)

    # Ordenar por mes el grafico 
    months_order = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    grouped_data_for_graph = grouped_data[grouped_data['Mes'].isin(months_order)].copy()
    grouped_data_for_graph['Mes'] = pd.Categorical(grouped_data_for_graph['Mes'], categories=months_order, ordered=True)
    grouped_data_for_graph = grouped_data_for_graph.sort_values('Mes')

    # Generar figura
    fig = go.Figure()

    fig.add_trace(go.Bar(x=grouped_data_for_graph['Mes'], y=grouped_data_for_graph['Tiem Inv'], name='Tiempo Invertido',marker=dict(
            color='#6C3483',        # Color de la barra
            line=dict(color='black', width=1.1)   # Borde de la barra
            )))
    fig.add_trace(go.Bar(x=grouped_data_for_graph['Mes'], y=grouped_data_for_graph['Tiem.fac'], name='Tiempo Facturado',marker=dict(
            color='#3498DB',           # Color de la barra
            line=dict(color='black', width=1.1)   # Borde de la barra
            )))

    return grouped_data.to_dict('records'), fig

if __name__ == '__main__':
    app.run_server(debug=True)