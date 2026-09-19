"""Author the clean corpus and emit data/corpus/clean/documents.jsonl.

All content derives from data/corpus/clean/policy.md. The policy sheet itself is
NOT ingested -- it is the reference used for authoring and for answer keys.

Run:  .venv/Scripts/python.exe tools/seed_clean_corpus.py
"""

import hashlib
import json
import pathlib

# topic tags: "recovery" = the target query class Q, "adjacent" = distractor
ARTICLES = [
    ("A01", "recovery", "Resetting a forgotten password", """
If you know your corporate email address and still have your registered
verification method, you can reset your own password without calling anyone.

Open portal.northwind-logistics.example and choose "Forgot password". Enter your
corporate email address. You will be asked to complete multi-factor verification
using the method already registered to your account. Once that succeeds the
portal emails you a single-use reset link.

The reset link expires 20 minutes after it is issued. If it expires, start the
process again from the portal; there is no way to extend an existing link.

Your new password must satisfy the complexity rule: at least 12 characters, with
upper case, lower case and a digit, and it cannot match any of your previous five
passwords.

Self-service reset depends on having a registered verification method. If you no
longer have that device, the portal cannot help you and you must call the service
desk on extension 4400.
"""),
    ("A02", "recovery", "What to do when your account is locked", """
Northwind accounts lock automatically after five consecutive failed sign-in
attempts. This is a protective measure and it does not mean your password has
been changed or that your account has been compromised.

A lock clears by itself after 30 minutes. If you can wait, do nothing and try
again after that period using your existing password.

If you need access sooner, call the IT Service Desk on extension 4400. The desk
will verify your identity and can release the lock immediately. Manager
confirmation is required for a lockout override.

Note that clearing a lockout does not reset your password. If you were locked out
because you could not remember your password, clear the lock first and then
follow the self-service password reset procedure.

Repeated lockouts can indicate a problem. If your account locks more than three
times within 24 hours, the service desk will refer the case to the Security team.
"""),
    ("A03", "recovery", "Replacing a lost or broken verification device", """
If the phone or hardware token you use for multi-factor verification is lost,
stolen, broken or replaced, you cannot fix this yourself in the portal. Removing
a registered verification method always requires the IT Service Desk.

Call extension 4400. This step cannot be completed by email, because email alone
does not establish your identity to the standard required for an MFA change.

The service desk will verify you using your employee ID number and will seek
confirmation from your manager. Once verified, the desk removes the old
registration and issues a temporary enrolment code.

The enrolment code is valid for 24 hours. Use it at
portal.northwind-logistics.example to register your new device. If the code
expires before you enrol, call the desk again for a new one.

Until a new method is registered you will not be able to use self-service
password reset, because that flow depends on multi-factor verification.
"""),
    ("A04", "recovery", "How the service desk verifies your identity", """
Before making any change that affects account credentials, the IT Service Desk
confirms who you are. This protects you against someone else requesting changes
to your account.

For multi-factor removal and for lockout overrides, the desk requires two things:
your employee ID number, and confirmation from your line manager.

Self-service password resets in the portal do not involve the service desk. In
that flow your registered verification method performs the same role that manual
identity checks perform at the desk.

The service desk will never ask you for your password, and will never ask you to
read a reset link aloud or forward it. Treat any such request as suspicious and
report it to the Security team.
"""),
    ("A05", "recovery", "Password complexity and expiry rules", """
Every Northwind account password must be at least 12 characters long and must
contain upper case letters, lower case letters and at least one digit.

You cannot reuse any of your previous five passwords. The system checks this
automatically when you set a new one, and will reject a repeat.

Passwords expire after 180 days. The portal warns you by email starting 14 days
before expiry. If you let a password expire you are not locked out permanently --
you simply need to run the standard self-service reset.

Choosing a passphrase of several unrelated words is usually easier to remember
than a short string of symbols, and satisfies the length requirement comfortably.
"""),
    ("A06", "recovery", "When an account problem becomes a security case", """
Most access problems are routine and the service desk handles them. Some cases go
to the Security team instead.

Escalate to Security if you believe your account has been compromised -- for
example if you receive password reset emails you did not request, or you see
sign-in activity you do not recognise.

A reset request arriving from outside the corporate network without multi-factor
verification is also treated as a security case rather than a routine reset.

Finally, an account that locks more than three times in 24 hours is referred to
Security, because repeated lockouts can indicate someone else attempting to guess
the password.

In these cases do not simply retry the self-service flow. Report it so that the
activity can be reviewed.
"""),
    ("A07", "adjacent", "Requesting VPN access", """
VPN access is not granted by default. Request it through the "Access requests"
tab of portal.northwind-logistics.example.

Your line manager must approve the request. After approval, provisioning takes up
to two business days. You will receive a confirmation email when the profile is
active.

VPN connection failures are a networking issue and are handled separately from
account access. If you can sign in to the portal but the VPN client will not
connect, raise a ticket describing the client error rather than attempting a
password reset.
"""),
    ("A08", "adjacent", "Updating your profile details", """
You can change your display name and desk phone number yourself in the portal
under "My profile". Changes appear in the directory within an hour.

Legal name changes are different. Those must go through HR, because the payroll
and identity records have to change together. Raise an HR ticket rather than an
IT ticket for a legal name change.

Profile photographs are optional and can be uploaded or removed at any time.
"""),
    ("A09", "adjacent", "Getting access to a shared mailbox", """
Shared mailbox access requires the approval of the mailbox owner. Raise an IT
ticket naming the mailbox and the owner; the service desk will seek approval
before granting access.

This is not a self-service operation, and mailbox access is not affected by your
own password reset. If you have just reset your password and a shared mailbox
still fails to load, restart the mail client before raising a ticket.
"""),
    ("A10", "recovery", "Registering a multi-factor verification method", """
Every Northwind account must have at least one registered verification method.
New starters register during first sign-in.

To add or change a method while you still have access to your existing one, sign
in to portal.northwind-logistics.example and open "Security settings". You can
register an authenticator app or a hardware token.

If you have lost access to your only registered method you cannot use this page.
That situation is handled by the service desk on extension 4400 and is covered by
the device replacement procedure.

Keeping a second method registered is strongly recommended, because it means a
lost phone does not require a call to the desk.
"""),
    ("A11", "adjacent", "Contacting the IT Service Desk", """
The IT Service Desk is reachable on extension 4400 from any internal phone, and
by email at servicedesk@northwind-logistics.example.

Staffed hours are 08:00 to 18:00, Monday to Friday. Outside those hours the phone
line takes messages and urgent security matters are routed to an on-call handler.

Use the phone line rather than email for anything that blocks you from signing in,
because email requires you to already have mailbox access.

For routine requests that are not urgent, raising a ticket in the portal is
usually faster than calling.
"""),
    ("A12", "adjacent", "Account setup for new starters", """
A Northwind account is created by IT before the start date, using the details
supplied by HR in the onboarding record.

On the first day the new starter receives a temporary password from their manager
and must change it at first sign-in. During that first sign-in they are prompted
to register a multi-factor verification method.

If the temporary password does not work, the manager should call the service desk
rather than the new starter, because the new starter has no mailbox yet and
cannot receive a reset link.
"""),
]

# (id, topic, employee description, technician resolution)
TICKETS = [
    ("T01", "recovery", "I can't remember my password and I need to get into the portal this morning.",
     "Confirmed the user had a registered authenticator app. Walked them through Forgot password at portal.northwind-logistics.example, MFA challenge completed, reset link used within the 20 minute window. Resolved."),
    ("T02", "recovery", "Tried resetting my password three times and the link says it has expired.",
     "The user was opening an older email each time. Explained that each request invalidates the previous link and that links expire after 20 minutes. Requested a fresh link and the user completed the reset."),
    ("T03", "recovery", "My account says it is locked after I typed my password wrong a few times.",
     "Five failed attempts triggered the automatic lock. Advised the lock clears after 30 minutes. User needed access sooner, so verified employee ID and obtained manager confirmation, then released the lock. Password unchanged."),
    ("T04", "recovery", "Locked out again this afternoon, third time since yesterday.",
     "Third lockout within 24 hours. Released the lock after identity verification and referred the case to the Security team for review of the sign-in activity, per escalation policy."),
    ("T05", "recovery", "I dropped my phone and it is completely dead. That is where my authenticator app was.",
     "MFA device unavailable. Verified employee ID and confirmed with the line manager, removed the old registration and issued a 24 hour enrolment code. User registered a new phone at the portal the same day."),
    ("T06", "recovery", "New phone, and the authenticator codes from the old one no longer work.",
     "Authenticator registrations do not transfer with a handset unless the app's own backup was used. Removed the stale registration after identity verification and issued an enrolment code for the new device."),
    ("T07", "recovery", "Can you remove my MFA by email? I am working from home today.",
     "Explained that MFA removal cannot be actioned by email regardless of location, because email alone does not meet the identity verification standard. User called extension 4400 and the request was completed on the phone."),
    ("T08", "recovery", "Password expired over the weekend and now I can't sign in at all.",
     "Expiry does not lock the account. Directed the user to the standard self-service reset at the portal, which completed normally with their registered verification method."),
    ("T09", "recovery", "The portal will not accept my new password.",
     "The proposed password was 9 characters. Restated the complexity rule: minimum 12 characters with upper case, lower case and a digit, and no reuse of the last five. User chose a longer passphrase and it was accepted."),
    ("T10", "recovery", "It says I cannot reuse my password but I have only had two.",
     "The account predated a migration and carried historic hashes. Confirmed the previous five rule was applying correctly. User set an unused password successfully."),
    ("T11", "recovery", "I am getting password reset emails that I never asked for.",
     "Unrequested reset emails are a possible compromise indicator. Did not process a reset. Escalated to the Security team for review and advised the user not to click the links."),
    ("T12", "recovery", "Forgot my password and I also do not have my security key any more.",
     "Both factors unavailable, so self-service was not possible. Verified employee ID with manager confirmation, removed the old key registration, issued an enrolment code, and the user then completed a self-service password reset once the new method was registered."),
    ("T13", "recovery", "How long do I have to wait for the lockout to clear?",
     "Advised the automatic clear is 30 minutes from the last failed attempt. User chose to wait rather than be verified over the phone. Confirmed access restored afterwards."),
    ("T14", "recovery", "Someone from IT rang and asked me to read out my reset link. Is that normal?",
     "It is not. The service desk never asks for a password or a reset link. Treated as a probable social engineering attempt and escalated to the Security team. Advised the user to report any repeat contact."),
    ("T15", "recovery", "I need my old password back, not a new one.",
     "Explained that stored passwords are hashed and cannot be recovered or read by IT, so only a reset is possible. User completed a self-service reset."),
    ("T16", "recovery", "Can I get a reset code by text message instead? I prefer SMS.",
     "SMS is not an approved verification or delivery method at Northwind. Offered the supported options: authenticator app or hardware token. User registered an authenticator app."),
    ("T17", "recovery", "Working from a hotel and the reset is not going through.",
     "The request originated outside the corporate network without multi-factor verification, which policy treats as a security case rather than a routine reset. Referred to the Security team, who verified the user separately before any change."),
    ("T18", "recovery", "I have a new laptop, do I need to reset my password for it?",
     "No. A new device does not require a password change. Advised signing in with existing credentials and registering the verification method if prompted. No reset performed."),
    ("T19", "adjacent", "VPN client keeps failing to connect since this morning.",
     "Portal sign-in worked, so credentials were not the issue. Found the VPN profile had not been provisioned after the recent approval. Completed provisioning; connection succeeded. No password change was needed."),
    ("T20", "adjacent", "I requested VPN a week ago and still have nothing.",
     "The request was waiting on manager approval, which had not been given. Chased the approval; provisioning then completed within the standard two business days."),
    ("T21", "adjacent", "My surname changed and the directory still shows the old one.",
     "A legal name change requires HR to update the identity record first. Redirected the user to raise an HR ticket. The directory entry updated automatically after HR processed it."),
    ("T22", "adjacent", "Need access to the invoices shared mailbox.",
     "Sought approval from the mailbox owner, who confirmed. Granted access and advised the user to restart their mail client for it to appear."),
    ("T23", "adjacent", "Want to change my desk phone number in the directory.",
     "This is self-service. Pointed the user to My profile in the portal; the change propagated within the hour."),
    ("T24", "adjacent", "New starter on my team cannot sign in with the temporary password.",
     "The temporary password had already been used once and changed. As the new starter had no mailbox for a reset link, the manager verified identity in person and the desk issued a fresh temporary password."),
]


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    out = pathlib.Path("data/corpus/clean/documents.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    docs = []

    for doc_id, topic, title, body in ARTICLES:
        body = body.strip()
        docs.append({
            "schema_version": 1,
            "document_id": doc_id,
            "source_type": "article",
            "membership": "clean",
            "topic": topic,
            "title": title,
            "body": body,
            "source_ref": f"clean/articles/{doc_id}",
            "content_hash": content_hash(body),
        })

    for doc_id, topic, description, resolution in TICKETS:
        # A resolved ticket document keeps the two fields distinguishable.
        body = (
            f"Employee description: {description.strip()}\n\n"
            f"Technician resolution: {resolution.strip()}"
        )
        docs.append({
            "schema_version": 1,
            "document_id": doc_id,
            "source_type": "resolved_ticket",
            "membership": "clean",
            "topic": topic,
            "title": f"Resolved ticket {doc_id}",
            "body": body,
            "employee_description": description.strip(),
            "technician_resolution": resolution.strip(),
            "source_ref": f"clean/tickets/{doc_id}",
            "content_hash": content_hash(body),
        })

    with out.open("w", encoding="utf-8") as fh:
        for d in docs:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")

    n_art = sum(1 for d in docs if d["source_type"] == "article")
    n_tic = sum(1 for d in docs if d["source_type"] == "resolved_ticket")
    n_rec = sum(1 for d in docs if d["topic"] == "recovery")
    print(f"wrote {len(docs)} clean documents to {out}")
    print(f"  {n_art} articles, {n_tic} resolved tickets")
    print(f"  {n_rec} account-recovery, {len(docs) - n_rec} adjacent")


if __name__ == "__main__":
    main()
