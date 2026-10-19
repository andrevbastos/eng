= Problema
\
#v(-1.5em)
O cliente (Uriarte) precisa de um sistema para armazenar e gerenciar as requisições e demandas da Assessoria Jurídica do IFC. Os órgãos envolvidos se organizam na seguinte hierarquia:
- Reitor;
- Procuradoria e Assessoria Jurídica;
- Pró-reitorias e setores (ProPessoas, Proad, Proep, etc.).

O Reitor assina todas as requisições. A Procuradoria emite pareceres, decidindo se um plano ou edital está de acordo com a legislação. A Assessoria Jurídica recebe as requisições, analisa, encaminha para a Procuradoria ou para o Reitor e redige os documentos finais.

Um exemplo do fluxo é a contratação de uma obra: são levantadas as empresas que atendem aos requisitos; entre elas, são selecionadas as 3 de menor preço e, destas, a que melhor se encaixa no projeto. A Procuradoria avalia se o plano está suficiente e assina; então a Assessoria escreve o edital. Até que a documentação esteja suficiente, há várias trocas de correções entre Procuradoria e Assessoria.

Muitas dúvidas levadas à Procuradoria já foram respondidas em pareceres anteriores. Como esses pareceres não ficam organizados, a mesma pergunta é feita novamente. Por isso, é necessário um banco de pareceres da Procuradoria, consultável pela Assessoria antes de abrir uma nova consulta.

Além disso, todas as demandas do Ministério Público chegam à Assessoria (ordens judiciais, reclamações, denúncias, ações, etc.). A Assessoria é obrigada a fazer um levantamento junto aos setores (subsídios) e dar uma resposta de defesa dentro do prazo. Hoje, todo esse processo é feito manualmente e registrado em papel, documentos, planilhas e e-mails espalhados. O banco deve conter, no mínimo, para cada demanda:
- Data de entrada da demanda
- Data limite para resposta
- O alvo, motivo, etc.
- Status da ação
- Por onde chegou (e-mail, SIGAA, pessoalmente e afins)
- Dados de como chegou (título do e-mail, quem enviou, quem recebeu)
- De onde vieram os subsídios (respostas)
- Todos os documentos anexados (PDF, DOCX, imagens, etc.)

== Arquitetura do sistema
\
#v(-1.5em)
Inicialmente, o cliente solicitou um sistema web, mas após uma conversa, foi decidido evitar o uso de web, por conta da manutenibilidade e segurança: um sistema web exige hospedagem, atualizações de segurança e uma equipe responsável pela manutenção contínua, que o setor não possui. Então, o sistema será desenvolvido como um aplicativo desktop, com banco de dados local (SQLite), sincronização opcional de documentos com o Google Drive e interface gráfica (GUI).

Nesta versão, o sistema é de uso único: um só usuário administrador opera o sistema, sem login, sem perfis e sem gestão de usuários. Trata-se de um CRUD de demandas, pareceres, subsídios, documentos e tags, com pesquisa, prazos e histórico de alterações. Uma futura versão multiusuário, com autenticação e controle de acesso por perfil, poderá ser desenvolvida depois, reaproveitando a camada de serviços.

O sistema focará em uso pseudomanual, ou seja, o usuário insere as informações manualmente e o sistema organiza e armazena tudo de forma automática. Funcionalidades como leitura de PDF, ligação ao Google Drive e e-mail automático são tratadas como requisitos excitantes (seção 2.4) e serão implementadas após os requisitos esperados.

== Resumo

O projeto tem como objetivo desenvolver um sistema para gerenciar requisições, demandas e pareceres da Assessoria Jurídica do IFC, centralizando informações e documentos, com histórico de alterações. Nesta versão, o sistema é de uso único, sem autenticação nem controle de acesso por perfil. O sistema será um aplicativo desktop, utilizando Python, SQLite e interface gráfica em CustomTkinter. Leitura de PDFs, integração com Google Drive e envio automático de e-mails serão implementados após as funcionalidades principais.

== Alterações desta versão

Esta versão reduz o escopo para uso único. Os IDs foram mantidos para preservar a rastreabilidade. Itens removidos permanecem na lista, marcados como "removido".

- Removidos: RS014 (usuários e perfis), RS021 (acesso restrito), RF012 (gestão de usuários e login), RF013 (ocultação por perfil), RNF008 (senhas e expiração de sessão), RNF009 (escritas concorrentes entre usuários), UsuarioService (RS015), campo usuario_id de Historico_Alteracoes (RS016).
- Alterados: RU008, RU010, RS001, RS015, RS016, RF014, RD003, RE003, RNF006 (sem alteração de meta, apenas contexto).
- Incluído: NR006 (não há múltiplos usuários, login nem perfis).

== Metas

As metas são os objetivos gerais que motivam o projeto. Diferente dos requisitos, elas não são verificadas diretamente no sistema, mas orientam a sua especificação; cada requisito da seção 2 contribui para uma ou mais metas.

- M001. Centralizar em um único local as demandas, pareceres, subsídios e documentos da Assessoria Jurídica.
- M002. Reduzir consultas repetidas à Procuradoria, reaproveitando pareceres já emitidos.
- M003. Substituir o controle em papel, planilhas e e-mails espalhados.
- M004. Evitar a perda de prazos de resposta às demandas do Ministério Público.

#set par(first-line-indent: 0em)
= Requisitos
== Etapa 1
*Requisitos de Usuário:*
- RU001 Registrar onde o documento está.
- RU002 Acesso aos documentos jurídicos e pareceres separadamente.
- RU003 Campo de observações.
- RU004 Sistema de tags para organizar os documentos.
- RU005 Um único espaço para pesquisa simples, com filtros.
- RU006 Todas as informações de uma demanda ou parecer visíveis na mesma tela, sem necessidade de abrir várias janelas.
- RU007 Sem preferência de cor, mas com tema escuro.
- RU008 Uso por um único usuário administrador, sem login e sem perfis. (Alterado; antes: mais de uma pessoa podia usar o sistema.)
- RU009 Saber quais demandas estão perto do prazo limite.
- RU010 Saber quando cada informação foi alterada e qual era o valor anterior. (Alterado; antes: saber quem alterou.)
- RU011 Abrir os documentos anexados direto pelo sistema ou pelo Google Drive.

== Etapa 2
*Requisitos de Sistema:*

RS001(RU001). Banco de dados SQLite em um único arquivo `.db`, armazenado em uma pasta escolhida pelo usuário (configurável), para armazenar todas as informações do sistema. Nesta versão, um único usuário deve abrir o arquivo por vez. (Alterado; antes: pasta compartilhada da Assessoria.)

RS002(RU002). Tabela Pareceres:
  - id: pk
  - numero: string única (número do parecer emitido pela Procuradoria)
  - assunto: string
  - conclusao: string
  - data: date
  - observacoes: string opt (RU003)

RS003(RU002). Tabela Demandas:
  - id: pk
  - titulo: string
  - alvo_motivo: string
  - data_entrada: date
  - data_limite: date
  - status: string ("Em análise", "Em andamento" (padrão), "Aguardando subsídios", "Aguardando Procuradoria", "Aguardando assinatura do Reitor", "Concluída")
  - segredo_justica: boolean (padrão falso; nesta versão é apenas informativo, ver RD003)
  - observacoes: string opt (RU003)
  - caminho_pasta: string opt
  - origem_canal: string ("E-mail", "SIGAA", "Presencial", "Ofício", "Outro")
  - origem_remetente: string
  - origem_destinatario: string
  - origem_documento: string opt (título do e-mail, número do ofício, etc.)

RS004(RU002). Tabela Subsídios:
  - id: pk
  - demanda_id: fk
  - setor_fonte: string
  - data_aquisicao: date
  - resposta: string

RS005(RU001, RU011). Tabela Documentos:
  - id: pk
  - parecer_id: fk opt
  - demanda_id: fk opt
  - subsidio_id: fk opt
  - caminho_arquivo: string
  - url_drive: string opt
  - tipo_arquivo: string
  - data_sincronizacao: datetime opt

RS006(RU004). Tabela Tags:
  - id: pk
  - nome: string única
  - cor: string (hexadecimal, ex.: `#3A7BD5`)

RS007(RU004). Tabela Tags_Demandas:
  - tag_id: fk
  - demanda_id: fk

RS008(RU004). Tabela Tags_Pareceres:
  - tag_id: fk
  - parecer_id: fk

RS009(RU004). Tabela Tags_Subsidios:
  - tag_id: fk
  - subsidio_id: fk

RS010(RU004). Tabela Tags_Documentos:
  - tag_id: fk
  - documento_id: fk

RS011(RU005). Pesquisa por um único campo de texto, comparado por fuzzy matching (similaridade de 0 a 100, limiar mínimo de 70) com os campos: id, titulo, alvo_motivo, numero, assunto, origem_remetente, observacoes e nomes das tags. A pesquisa pode ser combinada com filtros por status, tag, canal de origem e intervalo de datas (data_entrada e data_limite).

RS012(RU006). Interface com janela principal em abas (Demandas e Pareceres). Cada aba exibe a lista de resultados à esquerda e o painel de detalhes do item selecionado à direita, na mesma janela. Todos os campos de uma demanda (incluindo subsídios, documentos e tags) devem estar acessíveis no painel de detalhes sem abrir uma nova janela, em resolução mínima de 1366×768.

RS013(RU007). Tema escuro (modo "dark" do CustomTkinter) com contraste mínimo de 4,5:1 entre texto e fundo; cores além dos tons de cinza usadas apenas para tags, alertas de prazo e botões de ação.

RS014(RU008). Removido nesta versão. Não há tabela Usuarios, autenticação, perfis nem gestão de usuários. O sistema abre diretamente na janela principal. Uma versão multiusuário poderá reintroduzir este requisito.

RS015(RU006). Camada de serviços entre interface e banco de dados: DemandaService, ParecerService, SubsidioService, DocumentoService e TagService, cada um com as operações de criar, editar, buscar e excluir. A interface acessa o banco apenas através dessa camada, que aplica validações (RS017). (Alterado; UsuarioService e a verificação de permissões foram removidos.)

RS016(RU010). Tabela Historico_Alteracoes:
  - id: pk
  - tabela: string
  - registro_id: int
  - campo: string
  - valor_anterior: string opt
  - valor_novo: string opt
  - data_hora: datetime

(Alterado; o campo usuario_id foi removido. Se houver uma versão multiusuário, ele deverá ser reintroduzido.)

RS017(RU006). Validação de formulários: campos obrigatórios de Demanda (titulo, alvo_motivo, data_entrada, data_limite, status, origem_canal, origem_remetente, origem_destinatario) e de Parecer (numero, assunto, conclusao, data) são destacados quando vazios, e o botão de salvar fica desabilitado até serem preenchidos. O sistema rejeita numero de parecer repetido e data_limite anterior a data_entrada.

RS018(RU005). Os resultados de pesquisa são paginados em 50 itens por página. Sem resultados, o sistema exibe "Nenhum resultado encontrado" e um botão para limpar os filtros.

RS019(RU009). Demandas não concluídas com data_limite em até 5 dias são destacadas em amarelo na lista; demandas vencidas, em vermelho. Ao abrir o sistema, é exibido o total de demandas nessas duas situações.

RS020(RU011). Botão "Abrir" em cada documento, que abre o arquivo local no aplicativo padrão do sistema operacional, e botão "Abrir no Drive", disponível quando url_drive estiver preenchida, que abre o navegador nessa URL.

RS021(RU008). Removido nesta versão. Sem perfis, não há restrição de visualização por segredo de justiça no sistema (ver RD003).

RS022(RU001). Documentos anexados de até 50 MB por arquivo; arquivos maiores ou em formato não listado em RD001 são recusados com mensagem ao usuário.

*Requisitos de Domínio:*

RD001. Os documentos jurídicos chegam em diferentes formatos: PDF, DOC, DOCX, ODT, XLSX, TXT, EML (e-mail exportado), JPG e PNG.

RD002. Demandas do Ministério Público e ordens judiciais possuem prazo de resposta definido no próprio documento; por isso, a data limite é obrigatória em toda demanda.

RD003. Processos em segredo de justiça (art. 189 do Código de Processo Civil) só podem ser consultados por pessoas autorizadas. Nesta versão, o sistema não restringe a visualização desses processos, já que há um único usuário administrador. O campo segredo_justica é mantido apenas como informação. A restrição de acesso deverá ser implementada junto com a versão multiusuário. Até lá, cabe à Assessoria controlar quem tem acesso ao computador e ao arquivo .db.

RD004. Cada parecer da Procuradoria é identificado por um número único e serve como referência para consultas futuras sobre o mesmo assunto.

RD005. Toda requisição precisa da assinatura do Reitor para ser concluída; a demanda só pode passar para "Concluída" depois de passar por "Aguardando assinatura do Reitor".

RD006. As demandas chegam pelos canais: e-mail, SIGAA, presencialmente ou por ofício.

RD007. Os registros contêm dados pessoais de servidores, alunos e denunciantes, sujeitos à Lei Geral de Proteção de Dados (Lei nº 13.709/2018).

*Requisitos de Interface:*

RI001. Google Drive API (v3) para sincronização de documentos.
  - IN: caminho do arquivo local, credencial OAuth 2.0 da conta do usuário
  - OUT: arquivo enviado para a pasta configurada no Drive e URL do arquivo (gravada em url_drive)

== Etapa 3

*Requisitos Funcionais:*

RF001(RS003, RS017). O sistema deve permitir cadastrar, editar, consultar e excluir Demandas.

RF002(RS002, RS017). O sistema deve permitir cadastrar, editar, consultar e excluir Pareceres.

RF003(RS004). O sistema deve permitir cadastrar, editar e excluir Subsídios vinculados a uma Demanda.

RF004(RS005, RS022). O sistema deve permitir anexar documentos a uma Demanda, Parecer ou Subsídio, registrando o caminho do arquivo, e remover anexos.

RF005(RS006, RS007, RS008, RS009, RS010). O sistema deve permitir criar, editar e excluir tags (nome e cor) e associá-las ou desassociá-las de Demandas, Pareceres, Subsídios e Documentos.

RF006(RS011). O sistema deve pesquisar Demandas e Pareceres por um único campo de texto com fuzzy matching, atualizando a lista de resultados a cada termo digitado.

RF007(RS011). O sistema deve permitir adicionar e remover filtros por status, tag, canal de origem e intervalo de datas, combinados com a pesquisa de texto.

RF008(RS011). O sistema deve permitir localizar uma Demanda ou Parecer digitando seu id, título ou número.

RF009(RS018). O sistema deve paginar os resultados e, quando não houver resultados, exibir "Nenhum resultado encontrado" com a opção de limpar os filtros.

RF010(RS012). Ao clicar duas vezes em uma Demanda ou Parecer na lista, o sistema deve exibir todos os seus dados, subsídios, documentos e tags no painel de detalhes.

RF011(RS020). O sistema deve abrir um documento anexado no aplicativo padrão do sistema operacional e, quando houver URL do Drive, no navegador.

RF012(RS014). Removido nesta versão (login, gestão de usuários e controle de ações por perfil).

RF013(RS021). Removido nesta versão (ocultação de dados por perfil).

RF014(RS016). O sistema deve registrar cada criação, edição e exclusão (campo, valor anterior, valor novo, data e hora) e exibir o histórico no painel de detalhes da Demanda ou Parecer. (Alterado; o usuário autor deixou de ser registrado.)

RF015(RS019). O sistema deve destacar as demandas próximas do prazo ou vencidas e exibir o total delas ao iniciar.

RF016(RS017). O sistema deve validar os formulários antes de salvar, destacando campos obrigatórios vazios e recusando números de parecer repetidos e datas inválidas.

RF017(RI001). O sistema deve enviar ao Google Drive os documentos selecionados e gravar a URL resultante no documento.

*Requisitos não Funcionais:*

RNF001(RS001). O sistema deve ser desenvolvido como aplicação desktop em Python 3.12 ou superior, com banco SQLite acessado via ORM SQLAlchemy 2.

RNF002(RS012, RS013). A interface gráfica deve ser desenvolvida em CustomTkinter, em modo escuro, funcionando em resolução mínima de 1366×768.

RNF003(RS011). O fuzzy matching deve ser implementado com a biblioteca `rapidfuzz`.

RNF004(RI001). A integração com o Google Drive deve utilizar a biblioteca oficial `google-api-python-client`, com autenticação OAuth 2.0.

RNF005(REX002). A leitura de conteúdo de arquivos PDF deve utilizar as bibliotecas `pdfplumber` ou `pypdf`.

RNF006(RS011, RS018). A pesquisa deve retornar a primeira página de resultados em até 1 segundo com até 10.000 demandas cadastradas, e o painel de detalhes deve carregar em até 2 segundos.

RNF007(RS012). A partir da tela inicial, o usuário deve conseguir abrir um documento de uma demanda em no máximo 3 interações (pesquisar, clicar duas vezes na demanda, clicar em "Abrir").

RNF008(RS014, RD007). Removido nesta versão (senhas e expiração de sessão, pois não há autenticação).

RNF009(RS014). Removido nesta versão. Como há um único usuário, não é exigido o controle de escritas simultâneas entre usuários (ver NR006).

RNF010(RS022, RD001). O sistema deve aceitar documentos nos formatos de RD001 com até 50 MB por arquivo.

RNF011. O sistema deve ser distribuído como executável para Windows 10 e 11, gerado com PyInstaller, sem exigir a instalação do Python.

RNF012(RS001). O sistema deve criar automaticamente uma cópia de segurança do arquivo `.db` na primeira abertura de cada dia, mantendo as 7 cópias mais recentes.

== Etapa 4

*Requisitos Esperados:*

RE001(RF001, RF002, RF003, RF004). Cadastro de demandas, pareceres, subsídios e documentos em um único sistema.

RE002(RF005, RF006, RF007, RF008). Organização por tags e pesquisa por texto e filtros.

RE003(RF014). Histórico de alterações de cada demanda e parecer. (Alterado; antes: controle de acesso por perfil e histórico.)

RE004(RNF001, RNF002, RNF011). Aplicação desktop em tema escuro, com armazenamento local, sem servidor web.

*Não Requisitos:*

NR001. O sistema não será uma aplicação web e não terá hospedagem remota.

NR002. O sistema não terá quadro Kanban nem janelas flutuantes múltiplas.

NR003. O sistema não fará assinatura digital de documentos; a assinatura do Reitor continua sendo feita fora do sistema e apenas o status é registrado.

NR004. O sistema não importará automaticamente demandas do SIGAA, do SEI ou da caixa de e-mail; o cadastro é feito manualmente pelo usuário.

NR005. O sistema não terá versão para dispositivos móveis.

NR006. O sistema não terá, nesta versão, múltiplos usuários, login, perfis de acesso nem gestão de usuários. Também não há controle de escritas concorrentes entre usuários.

*Requisitos Excitantes:*

REX001(RF017, RNF004). Envio automático ao Google Drive dos documentos anexados, sem ação manual do usuário.

REX002(RNF005). Extração automática do texto dos PDFs anexados, para preencher campos do formulário e incluir o conteúdo na pesquisa.

REX003. Envio de e-mail (`smtplib`) aos usuários com a lista de demandas próximas do prazo (RS019). Nesta versão de uso único, o envio seria feito ao próprio administrador.
