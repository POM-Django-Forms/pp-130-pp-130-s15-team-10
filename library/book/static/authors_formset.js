document.addEventListener('DOMContentLoaded', function() {
    const formset = document.getElementById('authors-formset');
    const totalForms = formset.querySelector('[name="authors-TOTAL_FORMS"]');

    formset.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-author')) {
            e.preventDefault();
            let currentFormCount = parseInt(totalForms.value);
            let emptyForm = formset.querySelector('.author-row').cloneNode(true);

            emptyForm.querySelector('select').value = '';
            formset.appendChild(emptyForm);

            updateFormIndices(formset, currentFormCount);

            totalForms.value = currentFormCount + 1;
        }
        if (e.target.classList.contains('remove-author')) {
            e.preventDefault();
            if (formset.querySelectorAll('.author-row').length > 1) {
                e.target.closest('.author-row').remove();

                let currentFormCount = parseInt(totalForms.value) - 1;
                totalForms.value = currentFormCount;
                updateFormIndices(formset, currentFormCount);
            }
        }
    });

    function updateFormIndices(formset, count) {
        const forms = formset.querySelectorAll('.author-row');
        forms.forEach((formDiv, index) => {
            const select = formDiv.querySelector('select');
            select.name = `authors-${index}-author`;
            select.id = `id_authors-${index}-author`;
        });
    }
});
