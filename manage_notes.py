import Contacts
import objc
import sys

def get_all_contacts(store):
    keys = [
        # Keys to fetch. Without these we cannot read or modify the fields.
        Contacts.CNContactGivenNameKey,
        Contacts.CNContactFamilyNameKey,
        Contacts.CNContactNoteKey,
    ]
    
    request = Contacts.CNContactFetchRequest.alloc().initWithKeysToFetch_(keys)
    all_contacts = []
    
    # This acts as an Objective-C block callback. PyObjC translates it automatically.
    def fetch_handler(contact, stop_ptr):
        all_contacts.append(contact)
        
    # Triggering this implicitly requests the TCC privacy permission from macOS
    # the first time it is run.
    success, error = store.enumerateContactsWithFetchRequest_error_usingBlock_(
        request, None, fetch_handler
    )
    
    if error:
        print(f"Error fetching contacts: {error}")
        return []
        
    return all_contacts

def add_note_to_contact(store, contact, additional_note):
    """
    Appends an additional note to the contact's existing notes.
    """
    # 1. We must make a mutable copy of the Contact object in order to modify it
    mutable_contact = contact.mutableCopy()
    
    # 2. Get user's existing note (if any)
    existing_note = mutable_contact.note() or ""
    
    # 3. Append the new note (skip if we already added it earlier to prevent duplicates)
    if existing_note:
        if additional_note in existing_note:
            print(f"Skipping {contact.givenName()}: note already contains your new text.")
            return False
        new_note = existing_note + "\n\n" + additional_note
    else:
        new_note = additional_note
        
    # 4. Save the modified note back to the mutable contact
    mutable_contact.setNote_(new_note)
    
    # 5. Create a Save Request and ask the Contact Store to execute it
    save_request = Contacts.CNSaveRequest.alloc().init()
    save_request.updateContact_(mutable_contact)
    
    success, error = store.executeSaveRequest_error_(save_request, None)
    
    name = f"{contact.givenName() or ''} {contact.familyName() or ''}".strip()
    if success:
        print(f"Successfully added note: '{name}'")
        return True
    else:
        print(f"Failed to save note for '{name}': {error}")
        return False

def main():
    store = Contacts.CNContactStore.alloc().init()
    
    # Make sure we have permissions.
    status = Contacts.CNContactStore.authorizationStatusForEntityType_(Contacts.CNEntityTypeContacts)
    if status == Contacts.CNAuthorizationStatusDenied:
        print("❌ Access denied. Please go to your Mac's System Settings -> Privacy & Security -> Contacts.")
        print("Allow your Terminal (or IDE) to access Contacts.")
        sys.exit(1)
        
    print("Fetching contacts (A permission prompt may appear if this is your first time)...")
    contacts = get_all_contacts(store)
    print(f"Found {len(contacts)} contacts!")
    
    # =======================================================
    # EXAMPLE usage (Commented out for safety): 
    # =======================================================
    #
    # target_name = "John Doe"
    # new_note_content = "Keep in touch regarding blog scripts."
    # 
    # for contact in contacts:
    #     full_name = f"{contact.givenName() or ''} {contact.familyName() or ''}".strip()
    #     if full_name == target_name:
    #         add_note_to_contact(store, contact, new_note_content)
    #         break
    
    # Let's cleanly print 5 random contacts out so you know it works:
    print("\n--- Here is a sample of 5 contacts ---")
    for contact in contacts[:5]:
        full_name = f"{contact.givenName() or ''} {contact.familyName() or ''}".strip()
        note = contact.note() or "No note"
        print(f"Name: {full_name}\nCurrent Note: {note}\n")

if __name__ == "__main__":
    main()
