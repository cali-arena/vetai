"""
Módulo de geração automática de insights clínicos
"""

import pandas as pd
import numpy as np
from vetlib.preprocessing import FAIXAS_REFERENCIA


def gerar_insights_dataset(df):
    """
    Gera insights gerais sobre o dataset
    
    Args:
        df: DataFrame completo
        
    Returns:
        Lista de strings com insights
    """
    insights = []
    
    # 1. Distribuição de espécies
    if 'especie' in df.columns:
        especies_count = df['especie'].value_counts()
        especie_dominante = especies_count.index[0]
        pct_dominante = 100 * especies_count.iloc[0] / len(df)
        
        insights.append(
            f"🐾 **Distribuição de Espécies:** {especie_dominante} é a espécie mais comum "
            f"({pct_dominante:.1f}% dos casos)."
        )
    
    # 2. Diagnósticos mais frequentes
    if 'diagnostico' in df.columns:
        diag_count = df['diagnostico'].value_counts()
        top_3_diag = diag_count.head(3)
        
        texto = "📊 **Diagnósticos Mais Frequentes:** "
        for i, (diag, count) in enumerate(top_3_diag.items(), 1):
            pct = 100 * count / len(df)
            texto += f"{i}. {diag} ({pct:.1f}%); "
        
        insights.append(texto.rstrip("; "))
    
    # 3. Distribuição etária
    if 'idade_anos' in df.columns:
        idade_media = df['idade_anos'].mean()
        idade_mediana = df['idade_anos'].median()
        
        insights.append(
            f"📅 **Faixa Etária:** Idade média de {idade_media:.1f} anos "
            f"(mediana: {idade_mediana:.1f} anos)."
        )
    
    # 4. Distribuição de sexo
    if 'sexo' in df.columns:
        sexo_count = df['sexo'].value_counts()
        if 'M' in sexo_count and 'F' in sexo_count:
            pct_macho = 100 * sexo_count.get('M', 0) / len(df)
            insights.append(
                f"♂️♀️ **Distribuição de Sexo:** {pct_macho:.1f}% machos, "
                f"{100-pct_macho:.1f}% fêmeas."
            )
    
    # 5. Valores críticos/anormais
    exames_com_anormalidades = []
    
    for exame in ['creatinina', 'ureia', 'glicose', 'alt', 'ast']:
        if exame not in df.columns or 'especie' not in df.columns:
            continue
        
        n_anormais = 0
        for especie in df['especie'].unique():
            if especie not in FAIXAS_REFERENCIA:
                continue
            
            df_esp = df[df['especie'] == especie]
            min_ref, max_ref = FAIXAS_REFERENCIA[especie][exame]
            
            anormais = (df_esp[exame] < min_ref) | (df_esp[exame] > max_ref)
            n_anormais += anormais.sum()
        
        pct_anormal = 100 * n_anormais / len(df)
        if pct_anormal > 30:  # Threshold de relevância
            exames_com_anormalidades.append(f"{exame} ({pct_anormal:.1f}%)")
    
    if exames_com_anormalidades:
        insights.append(
            f"⚠️ **Valores Fora de Referência:** Exames com maior taxa de anormalidade: "
            f"{', '.join(exames_com_anormalidades)}."
        )
    
    # 6. Correlações interessantes
    exames_numericos = df.select_dtypes(include=[np.number]).columns.tolist()
    exames_principais = ['creatinina', 'ureia', 'alt', 'ast', 'glicose', 'hemoglobina']
    exames_numericos = [e for e in exames_principais if e in exames_numericos]
    
    if len(exames_numericos) >= 2:
        corr_matrix = df[exames_numericos].corr()
        
        # Encontrar correlações fortes (exceto diagonal)
        correlacoes_fortes = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.6:
                    correlacoes_fortes.append(
                        (corr_matrix.columns[i], corr_matrix.columns[j], corr_val)
                    )
        
        if correlacoes_fortes:
            texto = "🔗 **Correlações Fortes Detectadas:** "
            for feat1, feat2, corr in correlacoes_fortes[:3]:
                texto += f"{feat1} ↔ {feat2} ({corr:.2f}); "
            insights.append(texto.rstrip("; "))
    
    return insights


def gerar_insights_diagnostico(df, diagnostico):
    """
    Gera insights sobre um diagnóstico específico
    
    Args:
        df: DataFrame completo
        diagnostico: Nome do diagnóstico
        
    Returns:
        Lista de strings com insights
    """
    insights = []
    
    if 'diagnostico' not in df.columns:
        return insights
    
    df_diag = df[df['diagnostico'] == diagnostico]
    df_outros = df[df['diagnostico'] != diagnostico]
    
    if len(df_diag) == 0:
        return [f"⚠️ Nenhum caso de {diagnostico} encontrado no dataset."]
    
    # 1. Prevalência
    prevalencia = 100 * len(df_diag) / len(df)
    insights.append(
        f"📊 **Prevalência de {diagnostico}:** {len(df_diag)} casos ({prevalencia:.1f}% do dataset)."
    )
    
    # 2. Distribuição por espécie
    if 'especie' in df.columns:
        especies_diag = df_diag['especie'].value_counts()
        especie_mais_afetada = especies_diag.index[0]
        insights.append(
            f"🐾 **Espécie Mais Afetada:** {especie_mais_afetada} "
            f"({especies_diag.iloc[0]} casos)."
        )
    
    # 3. Faixa etária
    if 'idade_anos' in df.columns:
        idade_media_diag = df_diag['idade_anos'].mean()
        idade_media_outros = df_outros['idade_anos'].mean()
        
        if idade_media_diag > idade_media_outros + 1:
            insights.append(
                f"📅 **Faixa Etária:** Casos de {diagnostico} são mais comuns em animais mais velhos "
                f"(média: {idade_media_diag:.1f} anos vs {idade_media_outros:.1f} anos)."
            )
        elif idade_media_diag < idade_media_outros - 1:
            insights.append(
                f"📅 **Faixa Etária:** Casos de {diagnostico} são mais comuns em animais mais jovens "
                f"(média: {idade_media_diag:.1f} anos vs {idade_media_outros:.1f} anos)."
            )
    
    # 4. Exames característicos
    exames_principais = ['creatinina', 'ureia', 'alt', 'ast', 'glicose', 'hemoglobina', 'hematocrito']
    
    for exame in exames_principais:
        if exame not in df.columns:
            continue
        
        media_diag = df_diag[exame].mean()
        media_outros = df_outros[exame].mean()
        
        diff_pct = 100 * (media_diag - media_outros) / media_outros
        
        if abs(diff_pct) > 30:  # Diferença significativa
            if diff_pct > 0:
                insights.append(
                    f"🔬 **{exame.capitalize()}:** Significativamente **elevado** em casos de {diagnostico} "
                    f"({media_diag:.2f} vs {media_outros:.2f}, +{diff_pct:.1f}%)."
                )
            else:
                insights.append(
                    f"🔬 **{exame.capitalize()}:** Significativamente **reduzido** em casos de {diagnostico} "
                    f"({media_diag:.2f} vs {media_outros:.2f}, {diff_pct:.1f}%)."
                )
    
    # 5. Sintomas comuns
    sintomas = ['febre', 'apatia', 'perda_peso', 'vomito', 'diarreia', 'letargia', 
                'feridas_cutaneas', 'poliuria', 'polidipsia']
    
    sintomas_comuns = []
    for sintoma in sintomas:
        if sintoma not in df.columns:
            continue
        
        prevalencia_sintoma = df_diag[sintoma].mean()
        if prevalencia_sintoma > 0.5:  # Presente em >50% dos casos
            sintomas_comuns.append(f"{sintoma} ({100*prevalencia_sintoma:.0f}%)")
    
    if sintomas_comuns:
        insights.append(
            f"💊 **Sintomas Frequentes:** {', '.join(sintomas_comuns)}."
        )
    
    return insights


def gerar_alertas_valores_criticos(valores, especie='Canina'):
    """
    Gera alertas para valores críticos fora da faixa de referência
    
    Args:
        valores: Dict com valores de exames
        especie: Espécie do animal
        
    Returns:
        Lista de strings com alertas
    """
    alertas = []
    
    if especie not in FAIXAS_REFERENCIA:
        return alertas
    
    refs = FAIXAS_REFERENCIA[especie]
    
    # Definir níveis críticos (% fora da faixa)
    NIVEL_CRITICO = 0.5  # 50% fora da faixa
    NIVEL_MUITO_CRITICO = 1.0  # 100% fora da faixa
    
    for exame, valor in valores.items():
        if exame not in refs:
            continue
        
        if pd.isna(valor):
            continue
        
        min_ref, max_ref = refs[exame]
        
        if valor < min_ref:
            diff_pct = abs(valor - min_ref) / min_ref
            
            if diff_pct > NIVEL_MUITO_CRITICO:
                alertas.append(
                    f"🚨 **{exame.upper()}:** Valor MUITO BAIXO ({valor:.2f} vs {min_ref}-{max_ref}). "
                    f"Atenção imediata necessária!"
                )
            elif diff_pct > NIVEL_CRITICO:
                alertas.append(
                    f"⚠️ **{exame.capitalize()}:** Valor baixo ({valor:.2f} vs {min_ref}-{max_ref}). "
                    f"Monitoramento recomendado."
                )
        
        elif valor > max_ref:
            diff_pct = abs(valor - max_ref) / max_ref
            
            if diff_pct > NIVEL_MUITO_CRITICO:
                alertas.append(
                    f"🚨 **{exame.upper()}:** Valor MUITO ALTO ({valor:.2f} vs {min_ref}-{max_ref}). "
                    f"Atenção imediata necessária!"
                )
            elif diff_pct > NIVEL_CRITICO:
                alertas.append(
                    f"⚠️ **{exame.capitalize()}:** Valor alto ({valor:.2f} vs {min_ref}-{max_ref}). "
                    f"Monitoramento recomendado."
                )
    
    return alertas


def gerar_recomendacoes_clinicas(diagnostico_predito, probabilidade, valores_exames, especie='Canina'):
    """
    Gera recomendações clínicas baseadas no diagnóstico predito
    
    Args:
        diagnostico_predito: Diagnóstico mais provável
        probabilidade: Probabilidade do diagnóstico
        valores_exames: Dict com valores de exames
        especie: Espécie do animal
        
    Returns:
        Lista de strings com recomendações
    """
    recomendacoes = []
    
    # Disclaimer
    recomendacoes.append(
        "⚕️ **DISCLAIMER:** As recomendações abaixo são sugestões geradas automaticamente "
        "e NÃO substituem a avaliação clínica de um médico veterinário."
    )
    
    # Nível de confiança
    if probabilidade > 0.7:
        confianca = "Alta confiança"
    elif probabilidade > 0.4:
        confianca = "Confiança moderada"
    else:
        confianca = "Baixa confiança"
        recomendacoes.append(
            f"⚠️ {confianca} na predição ({100*probabilidade:.1f}%). "
            f"Considerar diagnósticos alternativos e exames complementares."
        )
    
    # Recomendações específicas por diagnóstico
    if 'Renal' in diagnostico_predito or 'renal' in diagnostico_predito.lower():
        recomendacoes.append(
            "🔬 **Avaliação Renal:** Monitorar creatinina, ureia e eletrólitos. "
            "Avaliar hidratação e considerar ultrassom renal."
        )
        
        if valores_exames.get('creatinina', 0) > FAIXAS_REFERENCIA[especie]['creatinina'][1]:
            recomendacoes.append(
                "💧 **Hidratação:** Creatinina elevada sugere necessidade de fluidoterapia "
                "e suporte à função renal."
            )
    
    elif 'Diabetes' in diagnostico_predito or 'diabetes' in diagnostico_predito.lower():
        recomendacoes.append(
            "🔬 **Controle Glicêmico:** Monitorar glicemia, frutosamina e cetonas urinárias. "
            "Avaliar necessidade de insulinoterapia."
        )
        
        recomendacoes.append(
            "🍎 **Manejo Dietético:** Considerar dieta específica para diabetes e controle de peso."
        )
    
    elif 'Hepat' in diagnostico_predito or 'hepat' in diagnostico_predito.lower():
        recomendacoes.append(
            "🔬 **Função Hepática:** Monitorar ALT, AST, fosfatase alcalina e bilirrubinas. "
            "Considerar ultrassom abdominal."
        )
        
        recomendacoes.append(
            "💊 **Suporte Hepático:** Avaliar necessidade de hepatoprotetores e dieta específica."
        )
    
    elif 'Anemia' in diagnostico_predito or 'anemia' in diagnostico_predito.lower():
        recomendacoes.append(
            "🔬 **Investigação de Anemia:** Realizar hemograma completo, contagem de reticulócitos "
            "e esfregaço sanguíneo. Investigar causas de perda/destruição/produção inadequada."
        )
    
    elif 'Leishmaniose' in diagnostico_predito or 'leishmaniose' in diagnostico_predito.lower():
        recomendacoes.append(
            "🔬 **Confirmação Diagnóstica:** Realizar testes sorológicos (ELISA, RIFI) "
            "e/ou parasitológicos (punção de medula/linfonodo)."
        )
        
        recomendacoes.append(
            "💊 **Tratamento Específico:** Considerar antimoniais pentavalentes, miltefosina "
            "e alopurinol. Monitoramento clínico e laboratorial contínuo."
        )
    
    # Recomendações gerais baseadas em valores
    if valores_exames.get('leucocitos', 0) > FAIXAS_REFERENCIA.get(especie, {}).get('leucocitos', (0, 999))[1]:
        recomendacoes.append(
            "🦠 **Leucocitose:** Investigar processo infeccioso ou inflamatório. "
            "Considerar exames microbiológicos se indicado."
        )
    
    # Acompanhamento
    recomendacoes.append(
        "📅 **Acompanhamento:** Reavaliar em 7-14 dias com novos exames laboratoriais "
        "e avaliação clínica completa."
    )
    
    return recomendacoes


def gerar_hipoteses_diagnosticas(valores_exames, sintomas, especie='Canina'):
    """
    Gera hipóteses diagnósticas baseadas em valores e sintomas
    
    Args:
        valores_exames: Dict com exames
        sintomas: Dict com sintomas (0/1)
        especie: Espécie
        
    Returns:
        Lista de hipóteses (strings)
    """
    hipoteses = []
    
    refs = FAIXAS_REFERENCIA.get(especie, FAIXAS_REFERENCIA['Canina'])
    
    # Avaliar função renal
    creat_alta = valores_exames.get('creatinina', 0) > refs['creatinina'][1]
    ureia_alta = valores_exames.get('ureia', 0) > refs['ureia'][1]
    
    if creat_alta and ureia_alta:
        hipoteses.append(
            "🔍 **Hipótese: Doença Renal** - Elevação de creatinina e ureia sugerem "
            "comprometimento da função renal."
        )
    
    # Avaliar função hepática
    alt_alta = valores_exames.get('alt', 0) > refs['alt'][1]
    ast_alta = valores_exames.get('ast', 0) > refs['ast'][1]
    
    if alt_alta and ast_alta:
        hipoteses.append(
            "🔍 **Hipótese: Hepatopatia** - Elevação de enzimas hepáticas (ALT, AST) "
            "sugere lesão hepatocelular."
        )
    
    # Avaliar diabetes
    glicose_alta = valores_exames.get('glicose', 0) > refs['glicose'][1] * 1.5
    poliuria = sintomas.get('poliuria', 0) == 1
    polidipsia = sintomas.get('polidipsia', 0) == 1
    
    if glicose_alta and (poliuria or polidipsia):
        hipoteses.append(
            "🔍 **Hipótese: Diabetes Mellitus** - Hiperglicemia associada a poliúria/polidipsia "
            "é sugestiva de diabetes."
        )
    
    # Avaliar anemia
    hb_baixa = valores_exames.get('hemoglobina', 999) < refs['hemoglobina'][0]
    ht_baixo = valores_exames.get('hematocrito', 999) < refs['hematocrito'][0]
    
    if hb_baixa or ht_baixo:
        letargia = sintomas.get('letargia', 0) == 1
        if letargia:
            hipoteses.append(
                "🔍 **Hipótese: Anemia** - Redução de hemoglobina/hematócrito com letargia "
                "sugere anemia clinicamente relevante."
            )
    
    if len(hipoteses) == 0:
        hipoteses.append(
            "✅ **Valores Dentro da Normalidade** - Não foram identificadas alterações "
            "laboratoriais significativas nos principais parâmetros avaliados."
        )
    
    return hipoteses






