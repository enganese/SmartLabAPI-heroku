# TEST | TEST | TEST | TEST | TEST | TEST | TEST | TEST | TEST | TEST | TEST | TEST | TEST #
# FOR MAXIM
# print(f"{result.years}")
# print(f"{result.debt_ebitda.aliases[0]}:", result.debt_ebitda.values)

# print(f"{result.ev_ebitda.aliases[0]}:", result.ev_ebitda.values)
# print(f"{result.p_e.aliases[0]}:", result.p_e.values)

# print(f"{result.p_s.aliases[0]}:", result.p_s.values)
# print(f"{result.roe.aliases[0]}:", result.roe.values)

# print(f"{result.net_margin.aliases[0]}:", result.net_margin.values)
# print(f"{result.p_bv.aliases[0]}:", result.p_bv.values)

# print(f"{result.revenue.aliases[0]}:", result.revenue.values)
# print(f"{result.dividend.aliases[0]}:", result.dividend.values)

# print(f"{result.fcf.aliases[0]}:", result.fcf.values)
# print(f"{result.operating_income.aliases[0]}:", result.operating_income.values)

# print(f"{result.net_income.aliases[0]}:", result.net_income.values)
# print(f"{result.ebitda.aliases[0]}:", result.ebitda.values)

# print(f"{result.number_of_shares.aliases[0]}:", result.number_of_shares.values)
# print(f"{result.net_debt.aliases[0]}:", result.net_debt.values)



# TEST | TEST | TEST | TEST | TEST | TEST | TEST | TEST | TEST | TEST | TEST | TEST | TEST #
def main():
    api = SmartLabAPI()
    result = api.get_data("ROSN", "q")

    import codecs
    for data in result:
        if not isinstance(data, list) and data.aliases[0] == "Держатель акции":
            print('\n\nData:')

            for info in data.data:
                print(json.dumps(info, indent=4, ensure_ascii=False))

            print('\n\nFor Graph:')

            print(data.for_graph)
            
            print(data.for_graph[0][0], data.for_graph[0][1])
            for info in data.for_graph[1:]:
                print(codecs.decode(info[0], "unicode-escape"), info[1])
        else:
            print(
                f"{data.aliases[0]}: {data.values}",
                f"\nАлиасы: {data.aliases}",
                f"\nДлина: {len(data.values)}",
                end="\n\n",
            ) if not isinstance(data, list) else print("Периоды:", data, "Длина:", len(data))


if __name__ == '__main__':
    main()