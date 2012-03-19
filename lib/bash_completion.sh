_cred()
{
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Cred's verbs
    opts="add get modify schema"

    # generate the appropriate completions, right now just for `cred get`
    case "${prev}" in
        get)
            local credentials=$(cred get)
            COMPREPLY=( $(compgen -W "${credentials}" -- ${cur}) )
            return 0
            ;;
        *)
        ;;
    esac

    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -F _cred cred
