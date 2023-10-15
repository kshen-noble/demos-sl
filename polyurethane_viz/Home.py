import streamlit as st
import pandas as pd
import plotly.express as px
#from query import *
import time
import joblib
from rdkit import Chem
from rdkit import Chem
from rdkit.Chem import Draw

#special imports
from streamlit_option_menu import option_menu 
from numerize.numerize import numerize
import mychem


# ===== Session Management =====
if "data" not in st.session_state:
    st.session_state["data"] = pd.read_csv("data/chemical_only_3output.csv")

if "model" not in st.session_state:
    model_name = "model3output"
    with open(f"data/{model_name}.joblib", 'rb') as f:
        st.session_state["model"] = joblib.load(f)


# ===== Main Page =====
st.set_page_config(page_title="Dashboard",page_icon="⚛",layout="wide")
st.header("Polyurethane Design")
st.markdown("##")

theme_plotly = 'streamlit' # None or streamlit

# Style
# with open('style.css')as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

#fetch data
#result = view_all_data()
#df=pd.DataFrame(result,columns=["Policy","Expiry","Location","State","Region","Investment","Construction","BusinessType","Earthquake","Flood","Rating","id"])

 
#load data and model
df = st.session_state["data"]
predictor = st.session_state["model"]



#sampInput = X_test[1:2].values
#result = predictor.predict(sampInput)[0]
#x,y,z = result



#side bar
st.sidebar.image("data/logo1.png",caption="NobleAI <> Internal")


def page_Charting():
    df["idx"] = df.index
    xchoice = st.selectbox("X-axis charting variable",
                           ['input_diol_nO', 'input_diol_nCO2', 'input_diol_nCO3', 'input_diol_nC',
       'input_diol_nCH3', 'input_iso_nC6H6', 'input_iso_nC6H12',
       'input_iso_nC', 'input_iso_nCH3', 'input_Ui', 'input_NCO/OH PP','output_Tm_ss'])
    #px.scatter(df,x="output_Tm_ss",y="output_E")

    #fig = px.box(df,x="output_E",points="all",hover_data=["idx","output_Tm_ss","input_Ui","input_NCO/OH PP"])
    fig = px.box(df,y="output_E",x=xchoice,points="all",hover_data=["idx","output_Tm_ss","input_Ui","input_NCO/OH PP"])

    #add trace
    #df2 = df.copy()
    #df2["output_E"] = df2["output_E"] + 2
    #px.box(df2,y="output_E",x=xchoice,points="all",hover_data=["idx","output_Tm_ss","input_Ui","input_NCO/OH PP"])

    fig.update_layout(showlegend=False)
    fig.update_layout(
        width=400,
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""---""")
    #st.data_editor(df)
    st.markdown("""---""")

diol_inputs = ['input_diol_nO', 'input_diol_nCO2', 'input_diol_nCO3', 'input_diol_nC','input_diol_nCH3']
diol_values = {k:0 for k in diol_inputs}
diol_values['input_diol_nC'] = 1

iso_inputs = ['input_iso_nC6H6', 'input_iso_nC6H12','input_iso_nC', 'input_iso_nCH3']
iso_values = {k:0 for k in iso_inputs}
iso_values['input_iso_nC'] = 1

other_inputs = ['input_Ui', 'input_NCO/OH PP']
other_values = {'input_Ui':0, 'input_NCO/OH PP':0}

def page_Design():
    total1,total2,total3=st.columns(3,gap='large')

    if "props" not in st.session_state:
        st.session_state["props"] = {
            "E":0.,
            "CO_free_W":0.,
            "Tm_ss":0.
        }
    if "smiles" not in st.session_state:
        st.session_state["smiles"] = [
            "CC",
            "O=C=NCN=C=O"
        ]

    props = st.session_state["props"]
    mcol1,mcol2,mcol3 = st.columns(3)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Design Soft Segment")
        for key in diol_inputs:
            if key.endswith("nC"):
                diol_values[key] = st.slider(key,2,10,step=1)
            else:
                diol_values[key] = st.slider(key,0,2,step=1)

    with col2:
        st.subheader("Design Hard Segment")
        for key in iso_inputs:
            if key.endswith("nC"):
                iso_values[key] = st.slider(key,1,4,step=1)
            else:
                iso_values[key] = st.slider(key,0,2,step=1)

    with col3:
        st.subheader("Other Controls")
        other_values['input_Ui'] = st.slider('input_Ui',0,1,step=1)
        other_values['input_NCO/OH PP'] = st.slider('input_NCO/OH PP',2.25,6.0)


    st.session_state["smiles"][0] = mychem.generate_diol(*[v for v in diol_values.values()])
    vals = [v for v in iso_values.values()]
    vals.append(other_values["input_Ui"])
    st.session_state["smiles"][1] = mychem.generate_iso(*vals)

    # make prediction
    tmp_dict = {}
    tmp_dict.update(diol_values)
    tmp_dict.update(iso_values)
    tmp_dict.update(other_values)
    tmp_df = pd.Series(tmp_dict).to_frame().transpose()

    props["E"], props["CO_free_W"], props["Tm_ss"] = predictor.predict(tmp_df)[0]
    st.session_state["props"].update(props)

    with total1:
        st.info('E')
        st.metric(label="",value=f"{props['E']:,.0f}")

    with total2:
        st.info('CO_free_W')
        st.metric(label="",value=f"{props['CO_free_W']:,.0f}")

    with total3:
        st.info('Tm_ss')
        st.metric(label="",value=f"{props['Tm_ss']:,.0f}")

    with mcol1:
        mol1 = st.session_state["smiles"][0]
        mol1 = Chem.MolFromSmiles(mol1)

        d1 = Chem.Draw.rdMolDraw2D.MolDraw2DSVG(300,200)
        d1.DrawMolecule(mol1)
        d1.FinishDrawing()
        svg1 = d1.GetDrawingText().replace('svg:','')
        st.image(svg1)
    with mcol2:
        mol2 = st.session_state["smiles"][1]
        mol2 = Chem.MolFromSmiles(mol2)

        d2 = Chem.Draw.rdMolDraw2D.MolDraw2DSVG(300,200)
        d2.DrawMolecule(mol2)
        d2.FinishDrawing()
        svg2 = d2.GetDrawingText().replace('svg:','')
        st.image(svg2)
#graphs

def page_Home():
    pass 

def page_Analyses():
    pass

def graphs():
    #total_investment=int(df_selection["Investment"]).sum()
    #averageRating=int(round(df_selection["Rating"]).mean(),2)
    
    #simple bar graph
    investment_by_business_type=(
        df_selection.groupby(by=["BusinessType"]).count()[["Investment"]].sort_values(by="Investment")
    )
    fig_investment=px.bar(
       investment_by_business_type,
       x="Investment",
       y=investment_by_business_type.index,
       orientation="h",
       title="<b> Investment by Business Type </b>",
       color_discrete_sequence=["#0083B8"]*len(investment_by_business_type),
       template="plotly_white",
    )


    fig_investment.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
     )

        #simple line graph
    investment_state=df_selection.groupby(by=["State"]).count()[["Investment"]]
    fig_state=px.line(
       investment_state,
       x=investment_state.index,
       y="Investment",
       orientation="v",
       title="<b> Investment by State </b>",
       color_discrete_sequence=["#0083b8"]*len(investment_state),
       template="plotly_white",
    )
    fig_state.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False))
     )

    left,right,center=st.columns(3)
    left.plotly_chart(fig_state,use_container_width=True)
    right.plotly_chart(fig_investment,use_container_width=True)
    
    with center:
      #pie chart
      fig = px.pie(df_selection, values='Rating', names='State', title='Regions by Ratings')
      fig.update_layout(legend_title="Regions", legend_y=0.9)
      fig.update_traces(textinfo='percent+label', textposition='inside')
      st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)
     


def sideBar():
    with st.sidebar:
        selected=option_menu(
            menu_title="Main Menu",
            options=["Home","Charting", "Live Design", "Analyses"],
            icons=["clipboard-data-fill","graph-up","eye"], #house
            menu_icon="cast",
            default_index=0
        )
    if selected == "Home":
        page_Home()
    if selected=="Live Design":
        #st.subheader(f"Page: {selected}")
        page_Design()
        # graphs()
    if selected == "Charting":
        page_Charting()
    if selected=="Analyses":
        #st.subheader(f"Page: {selected}")
        page_Analyses()
        # graphs()

sideBar()



#theme
hide_st_style=""" 

<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""



