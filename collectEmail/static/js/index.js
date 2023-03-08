document.onreadystatechange = function () {
    if (document.readyState == "complete") {
        InitApp();
    }
}

Element.prototype.isClassNamePresent = function (className) {
    return this.classList.contains(className)
}

Element.prototype.isActiveCollapseInButton = function () {
    return this.getAttribute('aria-expanded') == 'true'
}

const InitApp = () => {
    const btn_1 = document.querySelector('#btn_1')
    const btn_2 = document.querySelector('#btn_2')
    const modal_1 = document.querySelector('#set_email')
    const modal_2 = document.querySelector('#extra')

    if (!btn_1 || !btn_2 || !modal_1 || !modal_2) { return alert('Ocurrio un error al cargar la pagina') }

    btn_1.addEventListener('click', () => {

        if (btn_1.isClassNamePresent('bg-no-selected')) {
            btn_1.classList.remove('bg-no-selected')
            btn_2.classList.add('bg-no-selected')
        }

        if (modal_2.isClassNamePresent('show')) {
            modal_2.classList.remove('show')
            btn_2.setAttribute('aria-expanded', 'false')
        }

    })

    btn_2.addEventListener('click', () => {

        if (btn_2.isClassNamePresent('bg-no-selected')) {
            btn_2.classList.remove('bg-no-selected')
            btn_1.classList.add('bg-no-selected')
        }

        if (modal_1.isClassNamePresent('show')) {
            modal_1.classList.remove('show')
            btn_1.setAttribute('aria-expanded', 'false')
        }

    })

    /* Submit file multiply */
    const btn_3 = document.querySelector('#btn_3')
    const modal_3 = document.querySelector('#progress_files')

    btn_3.addEventListener('click', () => {
        const files = document.querySelector('#files')

        if (files.files.length == 0) return alert('No hay archivos para subir')

        modal_2.classList.remove('show')
        modal_3.classList.add('show')

        /* diable button 1,2 */
        btn_1.setAttribute('disabled', 'disabled')
        btn_2.setAttribute('disabled', 'disabled')

        sendFiles(Array.from(files.files))
    })

    const sendFiles = async (files) => {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
        const xmlhttp = new XMLHttpRequest()

        const formData = new FormData()
        files.forEach(file => {
            console.log(file)
            formData.append('files', file)
        })

        xmlhttp.upload.addEventListener('progress', (e) => {
            const progress = Math.round((e.loaded / e.total) * 80)
            const progress_bar = document.querySelector('#progress')
            progress_bar.style.width = `${progress}%`
            progress_bar.innerHTML = `${progress}%`
        })

        xmlhttp.addEventListener('load', (e) => {
            const progress_bar = document.querySelector('#progress')
            progress_bar.style.width = `100%`
            progress_bar.innerHTML = `100%`
            setTimeout(() => {
                const files = document.querySelector('#files')
                modal_3.classList.remove('show')
                btn_1.removeAttribute('disabled')
                btn_2.removeAttribute('disabled')
                modal_2.classList.add('show')
                files.value = ''
            }, 1000)
        })

        xmlhttp.open('POST', '/process/files')
        xmlhttp.setRequestHeader('X-CSRFToken', csrftoken)
        xmlhttp.send(formData)
    }
}
