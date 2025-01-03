import tomllib
import psycopg
import asyncio
import pandas as pd

def get_config():
    path = "config.toml"
    with open(path, "rb") as f:
        config = tomllib.load(f)

    return config


def get_db_conn_string():
    config = get_config()
    return(f"""
        dbname={config["db"]["db"]}
        user={config["db"]["user"]}
        password={config["db"]["password"]}
        host={config["db"]["host"]}
        port={config["db"]["port"]}
    """)


async def create_table():
    conn_str = get_db_conn_string()
    async with await psycopg.AsyncConnection.connect(conn_str) as aconn:
        async with aconn.cursor() as acur:
            await acur.execute("""
                CREATE TABLE IF NOT EXISTS exercises_manual (
                    date date not null,
                    activity text not null,
                    distance integer not null,
                    duration integer not null,
                    location text not null,
                    elsa integer not null,
                    ascent float not null,
                    pull integer not null,
                    weight float not null
                );
            """)


async def insert():
    conn_str = get_db_conn_string()
    async with await psycopg.AsyncConnection.connect(conn_str) as aconn:
        async with aconn.cursor() as acur:
            data = pd.read_csv("ski.csv")
            for index, row in data.iterrows():
                query = """
                    INSERT INTO exercises_manual (
                        date,
                        activity,
                        distance,
                        duration,
                        location,
                        elsa,
                        ascent,
                        pull,
                        weight
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                try:
                    await acur.execute(
                        query,
                        (
                            row.Date,
                            row.Activity,
                            row.Distance,
                            row.Time,
                            row.Location,
                            row.Elsa,
                            row.Elevation,
                            row.pull,
                            row.weight
                        )
                    )
                except Exception as e:
                    print(f"Error inserting: {e}")
    print("Done inserting")



async def main():
    await create_table()
    await insert()


if __name__ == "__main__":
    asyncio.run(main())