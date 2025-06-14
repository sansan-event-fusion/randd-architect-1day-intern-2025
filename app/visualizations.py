from streamlit_agraph import agraph, Node, Edge, Config

def personal_network_graph(person_info: dict, connections: list[dict]):
    """個人とそのつながりのネットワークグラフを描画する"""
    nodes = []
    edges = []
    nodes.append(Node(id=str(person_info['user_id']), label=person_info['full_name'], shape="star", size=25, color="#FF4B4B"))
    for person in connections:
        nodes.append(Node(id=str(person['user_id']), label=person['full_name']))
        edges.append(Edge(source=str(person_info['user_id']), target=str(person['user_id'])))
    config = Config(width="100%", height=400, directed=False, physics=True)
    agraph(nodes, edges, config)


def focused_corporate_network_graph(focus_company: dict, top_connections: list[dict], company_map: dict):
    """
    【新機能】中心企業とそのトップコネクションに焦点を当てたグラフを描画する
    """
    nodes = []
    edges = []
    
    focus_id = str(focus_company['company_id'])
    focus_name = focus_company['company_name']
    nodes.append(Node(id=focus_id, label=focus_name, shape="star", size=30, color="#FF4B4B"))

    # 2. トップコネクションのノードとエッジを追加
    for conn in top_connections:
        partner_id = str(conn['partner_id'])
        count = conn['count']
        partner_name = company_map.get(partner_id, f"不明な企業({partner_id})")
        
        # 不明な企業は色を変える
        node_color = "#6c757d" if not company_map.get(partner_id) else "#17a2b8"
        
        nodes.append(Node(id=partner_id, label=partner_name, size=15, color=node_color))
        edges.append(Edge(source=focus_id, target=partner_id, label=str(count), value=count))
        
    config = Config(width="100%", height=500, directed=False, physics=True,
                    node={'labelProperty':'label'},
                    link={'labelProperty': 'label', 'renderLabel': True})
    agraph(nodes, edges, config)

