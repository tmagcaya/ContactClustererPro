import os
import phonenumbers
from phonenumbers import geocoder
import us
from flask import Flask, render_template, request, jsonify, send_file
import io
import Contacts
import objc
import re

app = Flask(__name__)

def get_state_from_phone(number_str):
    """
    Parses a phone number string and attempts to deduce the US State Abbreviation (e.g. 'VA')
    """
    try:
        clean_num = "".join(filter(str.isdigit, number_str))
        if len(clean_num) == 10:
            clean_num = "+1" + clean_num
        elif len(clean_num) == 11 and clean_num.startswith("1"):
            clean_num = "+" + clean_num
        else:
            if not number_str.startswith("+"):
                clean_num = "+1" + clean_num
            else:
                clean_num = number_str

        parsed = phonenumbers.parse(clean_num, None)
        location = geocoder.description_for_number(parsed, "en")
        
        if not location:
            return ""
            
        # Parse output from geocoder. Often format: 'Virginia' or 'Fairfax, VA'
        if ", " in location:
            possible_state = location.split(", ")[-1]
            state_obj = us.states.lookup(possible_state)
            if state_obj:
                return state_obj.abbr
        else:
            state_obj = us.states.lookup(location)
            if state_obj:
                return state_obj.abbr
                
    except Exception as e:
        pass
    return ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/contacts')
def fetch_contacts():
    store = Contacts.CNContactStore.alloc().init()
    keys = [
        Contacts.CNContactIdentifierKey,
        Contacts.CNContactGivenNameKey,
        Contacts.CNContactFamilyNameKey,
        Contacts.CNContactOrganizationNameKey,
        Contacts.CNContactPhoneNumbersKey,
    ]
    request = Contacts.CNContactFetchRequest.alloc().initWithKeysToFetch_(keys)
    contact_list = []
    
    def fetch_handler(contact, stop_ptr):
        ident = contact.identifier()
        given = contact.givenName() or ""
        family = contact.familyName() or ""
        org = contact.organizationName() or ""
        
        phone_strings = []
        derived_state = ""
        
        if contact.phoneNumbers():
            for labeled_val in contact.phoneNumbers():
                val = labeled_val.value()
                if val:
                    num_str = val.stringValue()
                    phone_strings.append(num_str)
                    if not derived_state:
                        st = get_state_from_phone(num_str)
                        if st:
                            derived_state = st
                            
        contact_list.append({
            "id": ident,
            "name": f"{given} {family}".strip(),
            "company": org,
            "phones": phone_strings,
            "state": derived_state
        })
        
    store.enumerateContactsWithFetchRequest_error_usingBlock_(request, None, fetch_handler)
    
    # Sort array alphabetically by name
    contact_list.sort(key=lambda x: x['name'].lower())
    return jsonify(contact_list)

@app.route('/api/update', methods=['POST'])
def update_contacts():
    data = request.json
    contact_ids = data.get('contact_ids', [])
    category = data.get('category', '')
    
    if not category:
        return jsonify({"success": False, "error": "No category provided."})

    store = Contacts.CNContactStore.alloc().init()
    keys = [
        Contacts.CNContactIdentifierKey,
        Contacts.CNContactGivenNameKey,
        Contacts.CNContactFamilyNameKey,
        Contacts.CNContactOrganizationNameKey,
        Contacts.CNContactPhoneNumbersKey
    ]
    
    updated_count = 0
    for cid in contact_ids:
        predicate = Contacts.CNContact.predicateForContactsWithIdentifiers_([cid])
        found, error = store.unifiedContactsMatchingPredicate_keysToFetch_error_(predicate, keys, None)
        
        if found:
            contact = found[0]
            mutable = contact.mutableCopy()
            org = mutable.organizationName() or ""
            
            # Determine area code state for this specific contact
            state_str = ""
            if contact.phoneNumbers():
                for labeled_val in contact.phoneNumbers():
                    val = labeled_val.value()
                    if val:
                        num_str = val.stringValue()
                        s = get_state_from_phone(num_str)
                        if s:
                            state_str = s
                            break
                            
            # format [Dost - VA]
            tag = f"[{category}"
            if state_str:
                tag += f" - {state_str}"
            tag += "]"
            
            # Append only if this tag isn't already inside the company field
            if tag not in org:
                new_org = f"{org} {tag}".strip()
                mutable.setOrganizationName_(new_org)
                
                req = Contacts.CNSaveRequest.alloc().init()
                req.updateContact_(mutable)
                success, save_error = store.executeSaveRequest_error_(req, None)
                if success:
                    updated_count += 1

    return jsonify({"success": True, "updated": updated_count})

@app.route('/api/remove', methods=['POST'])
def remove_cluster():
    data = request.json
    contact_ids = data.get('contact_ids', [])
    
    store = Contacts.CNContactStore.alloc().init()
    keys = [Contacts.CNContactIdentifierKey, Contacts.CNContactOrganizationNameKey]
    
    updated_count = 0
    for cid in contact_ids:
        predicate = Contacts.CNContact.predicateForContactsWithIdentifiers_([cid])
        found, error = store.unifiedContactsMatchingPredicate_keysToFetch_error_(predicate, keys, None)
        if found:
            c = found[0]
            m = c.mutableCopy()
            org = m.organizationName() or ""
            # Regex to strip out any tags [Dost - ...] etc.
            new_org = re.sub(r'\s*\[.*?\]', '', org).strip()
            if new_org != org:
                m.setOrganizationName_(new_org if new_org else None)
                req = Contacts.CNSaveRequest.alloc().init()
                req.updateContact_(m)
                success, error = store.executeSaveRequest_error_(req, None)
                if success:
                    updated_count += 1
    return jsonify({"success": True, "updated": updated_count})

@app.route('/api/backup', methods=['GET'])
def backup_contacts():
    store = Contacts.CNContactStore.alloc().init()
    try:
        descriptor = Contacts.CNContactVCardSerialization.descriptorForRequiredKeys()
    except AttributeError:
        return jsonify({"success": False, "error": "vCard Serialization not supported in this environment. Please backup manually from the Contacts App."})
        
    request = Contacts.CNContactFetchRequest.alloc().initWithKeysToFetch_([descriptor])
    all_contacts = []
    
    def fetch_handler(contact, stop_ptr):
        all_contacts.append(contact)
        
    store.enumerateContactsWithFetchRequest_error_usingBlock_(request, None, fetch_handler)
    
    if not all_contacts:
        return jsonify({"success": False, "error": "No contacts found to back up."})
        
    # Serialize to standard vCard payload format
    vcard_data, error = Contacts.CNContactVCardSerialization.dataWithContacts_error_(all_contacts, None)
    if error:
        return jsonify({"success": False, "error": "Could not serialize to vCard: " + str(error)})
        
    py_bytes = bytes(vcard_data)
    
    return send_file(
        io.BytesIO(py_bytes),
        mimetype='text/vcard',
        as_attachment=True,
        download_name='mac_contacts_backup.vcf'
    )

if __name__ == '__main__':
    # Start web app on port 5001
    print("UI RUNNING! OPEN YOUR BROWSER TO: http://127.0.0.1:5001")
    app.run(debug=False, port=5001)
