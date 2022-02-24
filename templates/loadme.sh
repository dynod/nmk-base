# 
# !!! Load script generated by nmk-base plugin version {{ nmkBaseVersion }}, don't edit !!!
#

__checkSysDeps() {
    local cmd="${1}"
    local packages="${2}"
    
    # Command found?
    echo -n "Check ${cmd} "
    if test -z "$(which "${cmd}" 2>/dev/null || true)"; then
        echo "[missing]"
        NMK_APT_DEPS="${NMK_APT_DEPS} ${packages}"
    else
        echo "[OK]"
    fi
}
__installSysDeps() {
    # Something to install?
    if test -n "${NMK_APT_DEPS}"; then
        # Yes!
        echo "Installing missing packages:${NMK_APT_DEPS}"
        local sudo_prefix=""
        local install_suffix="-y"
        if test "$(id -u)" != "0"; then
            sudo_prefix="sudo "
            install_suffix=""
        fi
        
        # Repo refresh
        cmd="${sudo_prefix}apt update"
        echo "> ${cmd}"
        ${cmd} || return $?

        # Install
        cmd="${sudo_prefix}apt install${NMK_APT_DEPS} ${install_suffix}"
        unset NMK_APT_DEPS
        echo "> ${cmd}"
        ${cmd} || return $?
    fi
}

# Check system dependencies
{% for cmd in aptDeps.keys() %}__checkSysDeps {{ cmd }} "{{ aptDeps[cmd] }}"
{% endfor %}
# Perform installs if needed
__installSysDeps || return $?

# Clean useless stuff from terminal context
unset __checkSysDeps
unset __installSysDeps

# Create venv if not done yet
if test ! -d {{ venvName }}; then
    # Create it
    echo Create venv...
    {{ pythonForVenv }} -m venv {{ venvName }}

    # Load it
    source {{ venvName }}/bin/activate
    
    # Bootstrap it
    pip install pip wheel --upgrade {{ venvPipArgs }}

    # Install requirements
    pip install -r {{ venvRequirements }} {{ venvPipArgs }}

    # Patch it for nmk completion
    echo ' ' >> {{ venvName }}/bin/activate
    echo 'eval "$(register-python-argcomplete nmk)"' >> {{ venvName }}/bin/activate
fi

# Finally load venv
echo Load venv
source {{ venvName }}/bin/activate