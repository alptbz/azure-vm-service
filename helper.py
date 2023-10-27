
def generate_vm_name_out_of_email(email:str):
    user = email.split("@", 2)[0]
    user_parts = user.split(".", 2)
    if len(user_parts) != 2:
        raise Exception("email must be in format name.surname@example.com")
    clean_firstname = ''.join(e for e in user_parts[0] if e.isalpha())
    clean_surname = ''.join(e for e in user_parts[1] if e.isalpha())
    vm_name = f"{clean_firstname[:1]}{clean_surname[:7]}"
    return vm_name


