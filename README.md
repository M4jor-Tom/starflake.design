# starflake-design

Gameplay specification for Starflake: typed YAML in `spec/`, Gherkin in `features/`.

```shell
nix develop      # uv, Python, just
just test        # lint, fetch the pinned ontology, then validate spec/ and features/
just lint        # only lint and check the formatting of the Python files
just fetch       # only fetch the pinned ontology
```

`nix develop` enables the pre-push hook in `.githooks/`, which runs `just test`.
CI runs the same command on every pull request.

To upgrade the ontology, bump `ONTOLOGY_REF` in `design.lock` and run `just test`.
