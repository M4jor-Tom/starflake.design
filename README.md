# starflake-design

Gameplay specification for Starflake: typed YAML in `spec/`, Gherkin in `features/`.

```shell
nix develop      # uv, Python, just
just test        # fetch the pinned ontology, then validate spec/ and features/
```

Until the ontology's `v0.2.0` tag is pushed, fetch it from a local checkout:

```shell
STARFLAKE_ONTOLOGY_REPO=file://$PWD/../ontology just test
```

To upgrade the ontology, bump `ONTOLOGY_REF` in `design.lock` and run `just test`.
