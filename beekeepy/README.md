# Beekeepy

A high-level Python interface for interacting with a Beekeeper instance.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Object-Oriented Interface](#object-oriented-interface)
4. [Error Handling](#error-handling)
5. [Beekeeper Instance Management](#beekeeper-instance-management)
6. [Notes on Configuration](#notes-on-configuration)

## Introduction

Beekeepy is a Python library designed to offer a high-level object-oriented interface for interacting with a Beekeeper instance. Whether you want to start your own Beekeeper instance or connect to an existing one, Beekeepy simplifies the process while providing robust error handling and IDE integration through comprehensive type hinting.

## Features

- **Object-Oriented Interface**: Beekeepy provides a high-level, intuitive API for interacting with Beekeeper instances, allowing developers to manage and query Beekeeper with ease.
- **Synchronous and Asynchronous Support**: Beekeepy offers both synchronous and asynchronous versions of its API, allowing for flexible integration in projects using traditional blocking code or `asyncio` for non-blocking I/O.
- **Instance Management**: Beekeepy can either launch a new Beekeeper instance or connect to an already running instance.
- **IDE-Friendly with Full Typing**: Built with complete type annotations, Beekeepy is designed to integrate smoothly with modern IDEs, enhancing code navigation, auto-completion, and static analysis.
- **Exception Handling**: Beekeepy has built-in handling for common errors that may occur during interaction with Beekeeper. These exceptions are easy to catch and handle through dedicated exception classes.
- **No External Configuration Needed**: Beekeeper's binary is embedded directly into the package, making it ready to use out-of-the-box without additional configuration (Linux-only; Windows support is not planned).

## Object-Oriented Interface

Beekeepy offers a high-level, object-oriented interface, allowing you to interact with Beekeeper instances through Python objects. This simplifies many operations and reduces the complexity of integrating Beekeeper functionality into your applications.

Example usage:

```python
from beekeepy import Beekeeper, AsyncBeekeeper

# Connect to an existing instance (works on both sync and async)
async with await AsyncBeekeeper.remote_factory("http://localhost:8080") as beekeeper,
    await beekeeper.create_session() as session,
    await session.create_wallet(name="my_wallet", password="password") as wallet:
        public_key = await wallet.import_key(private_key=my_private_key)
        await wallet.sign_digest(digest=my_digest, public_key=public_key)

# Or create new local instance (works on both sync and async)
with Beekeeper.factory() as beekeeper,
    beekeeper.create_session() as session,
    session.create_wallet(name="my_wallet", password="password") as wallet:
        public_key = wallet.import_key(private_key=my_private_key)
        wallet.sign_digest(digest=my_digest, public_key=public_key)
```

With Beekeepy, you can manage Beekeeper processes easily, whether you're working with a local or remote instance.

## Error Handling

Beekeepy includes custom exception classes that handle common errors when interacting with Beekeeper. This allows you to catch and manage exceptions more effectively.

Example:

```python
from beekeepy import Beekeeper
from beekeepy.exceptions import InvalidPrivateKeyError

with Beekeeper.factory() as beekeeper,
    beekeeper.create_session() as session,
    session.create_wallet(name="my_wallet", password="password") as wallet:
        try:
            public_key = wallet.import_key(private_key="INVALID_PRIVATE_KEY")
        except InvalidPrivateKeyError as ex:
            handle_invalid_private_key()
```

Common errors such as connection issues, invalid operations, or timeout errors are wrapped in dedicated exception classes for better error handling and more readable code.

## Beekeeper Instance Management

Beekeepy is versatile in how it manages Beekeeper instances:

- **Launch a New Instance**: Start a Beekeeper instance directly from Python. The binary is bundled in the package, so no external setup is needed.
- **Connect to an Existing Instance**: Beekeepy allows you to connect to a Beekeeper instance that is already running, making it easy to integrate with existing infrastructure.

Example:

```python
# Launch a new instance of beekeeper and connect
client = await AsyncBeekeeper.factory()
# ...
await client.teardown()

# Or connect to an existing instance
client = Beekeeper.remote_factory("http://localhost:8080")
# ....
client.teardown()
```

> :warning: **Note**: If you use Beekeeper without `with` statement, remember to call `teardown` when you finish using it, so beekeeper will be properly close

## Notes on Configuration

Beekeepy comes with an embedded Beekeeper binary, so no additional configuration or setup is required to run the Beekeeper instance. Simply install the package, and you're ready to go!

> :warning: **Note**: The Beekeeper binary is compiled for Linux systems. There are no plans to support Windows.
