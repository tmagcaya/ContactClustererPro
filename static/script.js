document.addEventListener('DOMContentLoaded', () => {
    const tbody = document.getElementById('contacts-body');
    const selectAll = document.getElementById('select-all');
    const applyBtn = document.getElementById('apply-btn');
    const categorySelect = document.getElementById('category-select');
    const searchBox = document.getElementById('search-box');
    const contactCount = document.getElementById('contact-count');
    const removeBtn = document.getElementById('remove-btn');
    
    let allContacts = [];
    let currentFilter = 'all';
    let currentSortCol = 'name';
    let currentSortAsc = true;
    
    // Initial fetch from our Flask backend
    fetch('/api/contacts')
        .then(res => res.json())
        .then(data => {
            allContacts = data;
            updateView();
        })
        .catch(err => {
            tbody.innerHTML = `<tr><td colspan="5" style="color: #ff6b6b; text-align: center;">Failed to load contacts. Ensure permissions are granted!</td></tr>`;
        });
        
    function renderTable(contacts) {
        contactCount.innerText = contacts.length;
        tbody.innerHTML = '';
        
        if (contacts.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 30px;">No contacts found.</td></tr>`;
            return;
        }
        
        contacts.forEach(c => {
            const tr = document.createElement('tr');
            
            // Clean presentation for state
            const stateHtml = c.state 
                ? `<span class="state-badge">${c.state}</span>` 
                : `<span style="color:#666; font-size: 0.85rem;">Unknown</span>`;
            
            // Multiple phones styling
            const phonesHtml = c.phones.length > 0 
                ? c.phones.join('<br>') 
                : '<span style="color:#666;font-size:0.85rem">No phone</span>';
            
            let nameDisplay = c.name || '<i style="color:#666">Unnamed</i>';
            
            tr.innerHTML = `
                <td><input type="checkbox" class="contact-chk" value="${c.id}"></td>
                <td style="font-weight: 500;">${nameDisplay}</td>
                <td style="color: #aeb5be; font-size: 0.85rem">${phonesHtml}</td>
                <td>${stateHtml}</td>
                <td style="color: #8b949e; font-size: 0.85rem">${escapeHTML(c.company) || '<i style="color:rgba(255,255,255,0.2)">Unset</i>'}</td>
            `;
            tbody.appendChild(tr);
        });
        
        attachCheckboxListeners();
    }
    
    function escapeHTML(str) {
        if(!str) return "";
        return str.replace(/[&<>'"]/g, 
            tag => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                "'": '&#39;',
                '"': '&quot;'
            }[tag] || tag)
        );
    }

    function attachCheckboxListeners() {
        const checkboxes = document.querySelectorAll('.contact-chk');
        checkboxes.forEach(chk => {
            chk.addEventListener('change', updateApplyButtonState);
        });
        updateApplyButtonState();
    }
    
    selectAll.addEventListener('change', (e) => {
        const checkboxes = document.querySelectorAll('.contact-chk');
        checkboxes.forEach(chk => chk.checked = e.target.checked);
        updateApplyButtonState();
    });
    
    categorySelect.addEventListener('change', updateApplyButtonState);
    
    document.querySelectorAll('.filter-pill').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.dataset.filter;
            updateView();
        });
    });
    
    function updateView() {
        const query = searchBox.value.toLowerCase();
        let filtered = allContacts.filter(c => {
            let comp = (c.company || '').toLowerCase();
            let matchesPill = true;
            if (currentFilter === 'uncategorized') matchesPill = !comp.includes('[');
            else if (currentFilter === 'ulu') matchesPill = comp.includes('[ulu');
            else if (currentFilter === 'mtr') matchesPill = comp.includes('[mtr');
            else if (currentFilter === 'mentee') matchesPill = comp.includes('[mentee');
            else if (currentFilter === 'mentor') matchesPill = comp.includes('[mentor');
            else if (currentFilter === 'buddy') matchesPill = comp.includes('[buddy');
            else if (currentFilter === 'friend') matchesPill = comp.includes('[friend');
            
            if (!matchesPill) return false;
            
            if (query) {
                const nameMatch = (c.name || '').toLowerCase().includes(query);
                const stateMatch = (c.state || '').toLowerCase().includes(query);
                const phoneMatch = c.phones.some(p => p.includes(query));
                const compMatch = comp.includes(query);
                return nameMatch || stateMatch || phoneMatch || compMatch;
            }
            return true;
        });

        filtered.sort((a, b) => {
            let valA = (a[currentSortCol] || '').toLowerCase();
            let valB = (b[currentSortCol] || '').toLowerCase();
            if (valA < valB) return currentSortAsc ? -1 : 1;
            if (valA > valB) return currentSortAsc ? 1 : -1;
            return 0;
        });

        renderTable(filtered);
        updateSortIcons();
    }

    function updateSortIcons() {
        document.querySelectorAll('th.sortable').forEach(th => {
            const icon = th.querySelector('.sort-icon');
            if (th.dataset.sort === currentSortCol) {
                icon.innerHTML = currentSortAsc ? '↑' : '↓';
                icon.style.opacity = '1';
            } else {
                icon.innerHTML = '↕';
                icon.style.opacity = '0.3';
            }
        });
    }

    document.querySelectorAll('th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            if (currentSortCol === th.dataset.sort) {
                currentSortAsc = !currentSortAsc;
            } else {
                currentSortCol = th.dataset.sort;
                currentSortAsc = true;
            }
            updateView();
        });
    });

    searchBox.addEventListener('input', updateView);
    
    function updateApplyButtonState() {
        const selected = document.querySelectorAll('.contact-chk:checked').length;
        
        if (removeBtn) {
            removeBtn.disabled = selected === 0;
            removeBtn.innerText = selected > 0 ? `Remove Tags (${selected})` : 'Remove Tags From Selected';
        }
        
        if (selected > 0 && categorySelect.value) {
            applyBtn.disabled = false;
            applyBtn.innerText = `Apply to ${selected} Contact(s)`;
        } else {
            applyBtn.disabled = true;
            applyBtn.innerText = `Apply to Selected`;
        }
    }
    
    applyBtn.addEventListener('click', () => {
        const selectedIds = Array.from(document.querySelectorAll('.contact-chk:checked')).map(chk => chk.value);
        const category = categorySelect.value;
        
        if (category === 'blank') {
            if (removeBtn) removeBtn.click();
            return;
        }
        
        applyBtn.disabled = true;
        applyBtn.innerText = 'Applying...';
        
        fetch('/api/update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                contact_ids: selectedIds,
                category: category
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Remove checkbox selections after a successful apply
                selectAll.checked = false;
                
                // Re-fetch to show updated UI
                fetch('/api/contacts').then(r=>r.json()).then(newData => {
                    allContacts = newData;
                    // Reset search and redraw
                    searchBox.value = "";
                    updateView();
                    
                    setTimeout(() => alert(`Successfully updated ${data.updated} contacts!`), 100);
                });
            } else {
                alert("Error: " + data.error);
                updateApplyButtonState();
            }
        })
        .catch(err => {
            alert("Network error.");
            updateApplyButtonState();
        });
    });
    
    if (removeBtn) {
        removeBtn.addEventListener('click', () => {
            const selectedIds = Array.from(document.querySelectorAll('.contact-chk:checked')).map(chk => chk.value);
            if (!confirm(`Are you sure you want to remove all cluster tags from ${selectedIds.length} contacts?`)) return;
            
            removeBtn.disabled = true;
            removeBtn.innerText = 'Removing...';
            
            fetch('/api/remove', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({contact_ids: selectedIds})
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    selectAll.checked = false;
                    fetch('/api/contacts').then(r=>r.json()).then(newData => {
                        allContacts = newData;
                        updateView();
                        updateApplyButtonState();
                        setTimeout(() => alert(`Successfully stripped tags from ${data.updated} contacts!`), 100);
                    });
                }
            });
        });
    }
    
    const backupBtn = document.getElementById('backup-btn');
    if (backupBtn) {
        backupBtn.addEventListener('click', () => {
            window.location.href = '/api/backup';
        });
    }
});
