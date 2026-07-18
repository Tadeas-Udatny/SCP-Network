from extraction import get_SCP_items,pad_number

SCPs = get_SCP_items(2,50)

with open("test.csv", "w") as file:
    file.write("Source,Target,Weight\n")

    for scp in SCPs.values():
        for neighbour, weight in scp.connections.items():
            file.write(f"scp-{pad_number(scp.number)},scp-{pad_number(neighbour)},{weight}\n")