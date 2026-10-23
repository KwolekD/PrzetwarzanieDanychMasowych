1) Jaka jest różnica między `ENTRYPOINT` a `CMD`?

**Odpowiedź:** 
> Both CMD and ENTRYPOINT instructions define what command gets executed when running a container. There are few rules that describe their co-operation. 
> 1. Dockerfile should specify at least one of CMD or ENTRYPOINT commands.
> 2. ENTRYPOINT should be defined when using the container as an executable.
> 3. CMD should be used as a way of defining default arguments for an ENTRYPOINT command or for executing an ad-hoc command in a container.
> 4. CMD will be overridden when running the container with alternative arguments.

2) Jak każdą z powyższych opcji nadpisać podczas uruchamiania kontenera?

**Odpowiedź:** 
> CMD will be overridden when running the container with alternative arguments.

> You can override the ENTRYPOINT instruction using the docker run --entrypoint flag.

3) Jaka jest różnica między `ADD` a `COPY`?

**Odpowiedź:** 
>ADD and COPY are functionally similar. COPY supports basic copying of files into the container, from the build context or from a stage in a multi-stage build. ADD supports features for fetching files from remote HTTPS and Git URLs, and extracting tar files automatically when adding files from the build context.


4) Czy tylko jedno słowo kluczowe `FROM` może występować w pojedynczym pliku Dockerfile?

**Odpowiedź:** 
> FROM can appear multiple times within a single Dockerfile to create multiple images or use one build stage as a dependency for another. Simply make a note of the last image ID output by the commit before each new FROM instruction. Each FROM instruction clears any state created by previous instructions.

https://docs.docker.com/reference/dockerfile/
