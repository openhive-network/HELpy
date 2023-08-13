# Bug report

---
## Description

Here I place description of bug

---
## [Minimal reproducible example](https://en.wikipedia.org/wiki/Minimal_reproducible_example)

Here i paste code or put link to file with MRE

---
## Platform Info

#### Python Version (`python --version`):
#### HTP Commit (`git rev-parse HEAD`):
#### Schema Commit (`git -C schemas rev-parse HEAD`):
#### OS version (for linux: `lsb_release -a`):

---
## Standard Checks

- [ ] I am using newest version of this repo
- [ ] I have proper schema version (run `git submodule update --init --recursive`)
- [ ] I am connecting to working service (for hived try `curl -s --data '{"jsonrpc":"2.0", "method":"database_api.get_config", "id":1}' address-of-node-i-am-connecting-to`)

---
