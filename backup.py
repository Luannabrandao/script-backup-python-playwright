import asyncio
import os
from playwright.async_api import async_playwright

# --- CONFIGURAÇÕES GENÉRICAS DO SISTEMA (PORTFÓLIO) ---
URL_LOGIN = "https://link_do_sistema_exemplo.com.br/login"
GRUPO_EMPRESA = "nome_do_grupo_exemplo"

# Pasta local e isolada que o robô usará para armazenar os cookies da sessão de teste
CAMINHO_PERFIL_ROBO = "./perfil_automacao_sistema"
os.makedirs(CAMINHO_PERFIL_ROBO, exist_ok=True)

# Árvore completa de relatórios para mapeamento sequencial
RELATORIOS = [
    "Por dia",
    "Por Pagamentos",
    "Por canal de vendas",
    "Por canal x loja",
    "Por loja",
    "Cancelamentos",
    "Em detalhes",
    "Produtos (opções)",
    "Produtos",
]

# Escopo temporal do projeto de extração
ANOS = [2023, 2024, 2025, 2026]

# Lista fictícia de unidades/lojas para demonstração no portfólio
LOJAS = [
    "Unidade_A_Teste",
    "Unidade_B_Teste",
    "Unidade_C_Teste",
]

# --- MAPEAMENTO DE SELETORES EM CAMADAS ---
SELETOR_INPUT_LOGIN_LOJA = "input[placeholder='Loja']"
SELETOR_BOTAO_LOGIN_COMO = "button.btn-success:has-text('Fazer login como')"
SELETOR_MENU_PAI = "text=Relatórios de Vendas"

# Mapeamento por índice para dropdowns que compartilham a mesma classe CSS
SELETORES_DROPDOWNS = "div.css-6jjltg input"

SELETOR_CAMPOS_DATA = "input.DateInput_input_1"
SELETOR_BOTAO_FILTRAR = "button:has-text('Filtrar')"
SELETOR_BOTAO_EXPORTAR = "button.react-bs-table-csv-btn"
TEXTO_SEM_RESULTADOS = "text=Nenhum resultado encontrado"


async def executar_maratona_relatorios():
    async with async_playwright() as p:
        print("🌐 Inicializando navegador com perfil persistente seguro...")

        # Instancia o navegador simulando um ambiente de produção limpo
        context = await p.chromium.launch_persistent_context(
            user_data_dir=CAMINHO_PERFIL_ROBO,
            headless=False,
            args=["--start-maximized"],
        )

        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(URL_LOGIN)

        # Automação do primeiro estágio do formulário de login (Identificação do Grupo)
        try:
            await page.wait_for_selector(SELETOR_INPUT_LOGIN_LOJA, timeout=5000)
            print(f"✍️ Inserindo identificador do grupo: {GRUPO_EMPRESA}")
            await page.fill(SELETOR_INPUT_LOGIN_LOJA, GRUPO_EMPRESA)
            await page.wait_for_timeout(300)
            await page.click(SELETOR_BOTAO_LOGIN_COMO)
        except:
            print("👋 Tela inicial de grupo não detectada (Sessão já ativa).")

        # Delay estratégico para autenticação manual via MFA/OAuth e bypass de pop-ups iniciais
        print("\n⏳ Aguardando 30 segundos para autenticação manual e carga do painel...")
        await page.wait_for_timeout(30000)

        # === 1º LOOP: NAVEGAÇÃO ENTRE RELATÓRIOS (MENU LATERAL) ===
        for relatorio in RELATORIOS:
            print(f"\n📂 [PROCESSO] Acessando módulo: {relatorio}")

            try:
                await page.click(SELETOR_MENU_PAI, force=True)
                await page.wait_for_timeout(800)
                await page.click(
                    f"a.nav-link:has-text('{relatorio}')", force=True
                )
                print(f"✅ Módulo '{relatorio}' carregado.")
                await page.wait_for_timeout(3000)
            except Exception as e:
                print(f"❌ Falha de navegação no módulo '{relatorio}': {e}")
                continue

            # === 2º LOOP: FILTRAGEM POR ESCOPO TEMPORAL (ANOS) ===
            for ano in ANOS:
                data_inicio = f"01/01/{ano}"
                data_fim = f"31/12/{ano}"
                print(f"\n📅 [DATA] Definindo janela temporal para o ano: {ano}")

                # Estrutura de subdiretórios dinâmica para persistência dos dados
                pasta_destino = f"./arquivos_extraidos/{relatorio.replace(' ', '_')}/{ano}"
                os.makedirs(pasta_destino, exist_ok=True)

                # === 3º LOOP: ITERAÇÃO SOBRE AS UNIDADES DE NEGÓCIO (LOJAS) ===
                for loja in LOJAS:
                    print(f"  🏪 [TARGET] Processando filtros para: {loja}...")

                    try:
                        # Resolução de escopo do Dropdown de Unidades (Índice 1 garante o elemento correto)
                        dropdown_lojas = page.locator(
                            SELETORES_DROPDOWNS
                        ).nth(1)
                        await dropdown_lojas.click()
                        await page.wait_for_timeout(300)

                        # Sanitização do input antes da inserção do novo argumento
                        await page.keyboard.press("Control+A")
                        await page.keyboard.press("Backspace")
                        await dropdown_lojas.fill(loja)
                        await page.wait_for_timeout(500)
                        await page.keyboard.press("Enter")
                        await page.wait_for_timeout(500)

                        # Manipulação e formatação dos inputs de data do DatePicker
                        campos_data = page.locator(SELETOR_CAMPOS_DATA)

                        # Inserção da Data Inicial
                        await campos_data.nth(0).click()
                        await page.keyboard.press("Control+A")
                        await page.keyboard.press("Backspace")
                        await campos_data.nth(0).fill(data_inicio)
                        await page.wait_for_timeout(200)

                        # Inserção da Data Final
                        await campos_data.nth(1).click()
                        await page.keyboard.press("Control+A")
                        await page.keyboard.press("Backspace")
                        await campos_data.nth(1).fill(data_fim)
                        await page.wait_for_timeout(500)

                        # Submissão dos filtros de busca
                        await page.click(SELETOR_BOTAO_FILTRAR)
                        print("     ⏳ Aguardando processamento da requisição...")
                        await page.wait_for_timeout(3000)

                        # Validação lógica de conteúdo para prevenção de downloads corrompidos/vazios
                        if await page.locator(TEXTO_SEM_RESULTADOS).is_visible():
                            print(
                                f"     ⚠️ [IGNORADO] Sem movimentação comercial para {loja} em {ano}."
                            )
                        else:
                            print(
                                f"     ✅ [DATA FOUND] Iniciando stream de download do arquivo CSV..."
                            )

                            # Captura e tratamento assíncrono do evento de download do browser
                            async with page.expect_download() as download_info:
                                await page.click(SELETOR_BOTAO_EXPORTAR)

                            download = await download_info.value

                            # Padronização de nomenclatura de arquivos estruturados
                            nome_arquivo = f"{loja.replace(' ', '_')}_{ano}.csv"
                            caminho_salvamento = os.path.join(
                                pasta_destino, nome_arquivo
                            )

                            await download.save_as(caminho_salvamento)
                            print(
                                f"     💾 Dataset salvo com sucesso: {caminho_salvamento}"
                            )

                    except Exception as erro_loja:
                        print(
                            f"     ❌ [EXCEPTION] Falha na extração da unidade {loja}: {erro_loja}"
                        )
                        continue

        print("\n🏆 pipeline de extração executado com sucesso!")
        await context.close()


if __name__ == "__main__":
    # Execução do loop de eventos assíncronos do script
    asyncio.run(executar_maratona_relatorios())