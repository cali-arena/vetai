#!/usr/bin/env python3
"""
Teste simples para verificar se o sistema de predição está funcionando
"""

from vetlib.simple_diagnosis import gerar_hipoteses_simples

def test_prediction():
    print("🧪 Testando sistema de predição...")
    
    # Dados de teste
    sintomas = {
        'poliuria': 1,
        'polidipsia': 1,
        'letargia': 1
    }
    
    exames = {
        'creatinina': 3.0,
        'glicose': 20,
        'ureia': 150
    }
    
    especie = 'Canina'
    
    print(f"Sintomas: {sintomas}")
    print(f"Exames: {exames}")
    print(f"Espécie: {especie}")
    print("-" * 50)
    
    try:
        # Testar sistema simples
        resultados = gerar_hipoteses_simples(sintomas, exames, especie)
        
        print(f"✅ Sistema funcionando! {len(resultados)} hipóteses geradas:")
        
        for i, resultado in enumerate(resultados, 1):
            print(f"\n{i}. {resultado['diagnostico']}")
            print(f"   Score: {resultado['score']}")
            print(f"   Prioridade: {resultado['prioridade']}")
            print(f"   Tipo: {resultado['tipo']}")
            
            if 'criteria' in resultado:
                print("   Critérios:")
                for criterio in resultado['criteria']:
                    print(f"     • {criterio}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_prediction()
    if success:
        print("\n🎉 Sistema de predição está funcionando corretamente!")
    else:
        print("\n💥 Sistema de predição tem problemas!")


