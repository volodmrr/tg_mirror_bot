from .main import main, client

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())