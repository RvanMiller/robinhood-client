# Robinhood API Bruno Collection

## What is Bruno?
Bruno is an open-source API client for testing, debugging, and documenting APIs. It provides a fast, privacy-focused alternative to tools like Postman, allowing you to organize API requests in collections and work with them locally.

## Purpose of This Collection
This Bruno collection contains organized requests for the unofficial Robinhood API. It is designed to:
- Help developers test and explore Robinhood endpoints
- Document authentication and trading flows
- Accelerate development and debugging of the `robinhood-client` Python library

## How to Import This Collection into Bruno
1. Open Bruno and select your workspace.
2. Click the "+" button and choose "Import Collection".
3. Select the `collection.bru` file in this folder.
4. The Robinhood API requests will appear, organized by service (Account, Auth, Crypto, etc).

## How to Log In (Authentication)
Refer to the documentation in `Auth/` for details on the login flow. The typical steps are:

## Notes for Development
- This collection is intended for local development and debugging only.
- The requests mirror the endpoints and flows used in the `robinhood-client` Python library.
- You can use this collection to validate request/response formats, test authentication, and explore new endpoints before implementing them in code.

---
For more details on the Robinhood API and this client, see the main project [README](../../README.md).
