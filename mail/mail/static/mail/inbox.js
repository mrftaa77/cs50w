document.addEventListener('DOMContentLoaded', function () {
    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', () => compose_email());

    document.querySelector('#compose-form > input[type="submit"]').addEventListener('click', (event) => {
        event.preventDefault();
        send_email(
            document.querySelector('#compose-recipients').value,
            document.querySelector('#compose-subject').value,
            document.querySelector('#compose-body').value,
        );
    });

    // By default, load the inbox
    load_mailbox('inbox');
});

function compose_email() {
    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
    document.querySelector('#email-view').style.display = 'none';

    // Clear out composition fields
    const recipientsEl = document.querySelector('#compose-recipients');
    const subjectEl = document.querySelector('#compose-subject');
    const messageBodyEl = document.querySelector('#compose-body');

    [recipientsEl.value, subjectEl.value, messageBodyEl.value] = ['', '', ''];
}

function send_email(recipients, subject, messageBody) {
    fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
            recipients: recipients,
            subject: subject,
            body: messageBody,
        }),
    })
        .then((response) => response.json())
        .then(() => {
            load_mailbox('sent');
        });
}

function load_mailbox(mailbox) {
    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'none';

    // Show the mailbox name
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

    fetch(`/emails/${mailbox}`)
        .then((response) => response.json())
        .then((emails) => {
            list_emails(emails);
        });
}

function list_emails(emails) {
    const emailsView = document.querySelector('#emails-view');
    if (document.querySelector('.email-list')) document.querySelector('.email-list').remove();
    const emailList = document.createElement('div');
    emailList.classList.add('container', 'email-list');
    const emailListTitle = document.createElement('div');
    emailListTitle.classList.add('row', 'text-primary', 'border-bottom', 'border-primary', 'py-3', 'email-list__title');

    ['From', 'Subject', 'Date'].forEach((label, index) => {
        const emailListListCol = document.createElement('div');
        emailListListCol.classList.add('email-list__title-col');
        emailListListCol.innerHTML = label;
        if (index === 1) {
            emailListListCol.classList.add('col-6');
        } else {
            emailListListCol.classList.add('col');
        }
        emailListTitle.append(emailListListCol);
    });
    emailList.append(emailListTitle);

    emails.forEach((email) => {
        const emailListItem = document.createElement('div');
        emailListItem.classList.add('row', 'border', 'rounded', 'mt-3', 'py-3', 'email-list__item');
        emailListItem.dataset.emailId = email.id;
        emailListItem.addEventListener('click', () =>
            view_email(email.id, document.querySelector('#emails-view>h3').innerHTML !== 'Sent'),
        );
        ['sender', 'subject', 'timestamp'].forEach((property, index) => {
            const emailListItemCol = document.createElement('div');
            emailListItemCol.classList.add('email-list__item-col');
            if (index === 1) {
                emailListItemCol.classList.add('col-6');
            } else {
                emailListItemCol.classList.add('col');
            }
            if (email['read']) {
                emailListItem.classList.add('bg-dark-subtle');
            } else {
                emailListItem.classList.add('bg-light-subtle');
            }
            emailListItemCol.innerHTML = email[property];
            emailListItem.append(emailListItemCol);
        });
        emailList.append(emailListItem);
    });

    emailsView.append(emailList);
}

async function view_email(emailId, showReply) {
    document.querySelectorAll('.email-list__item').forEach((element) => element.remove()),
        (document.querySelector('#emails-view').style.display = 'none');
    document.querySelector('#compose-view').style.display = 'none';
    const emailView = document.querySelector('#email-view');
    emailView.style.display = 'block';

    const email = await get_email(emailId);

    document.querySelector('#email-from').value = email.sender;
    document.querySelector('#email-recipients').value = email.recipients.join(', ');
    document.querySelector('#email-subject').value = email.subject;
    document.querySelector('#email-body').value = email.body;
    document.querySelector('#email-timestamp>pre').innerHTML = email.timestamp;

    if (showReply) {
        const replyBtn = document.querySelector('#email-reply-btn');
        replyBtn.replaceWith(replyBtn.cloneNode(true));
        const newReplyBtn = document.querySelector('#email-reply-btn');
        newReplyBtn.style.display = 'block';
        newReplyBtn.addEventListener('click', () => {
            const replySubject = email.subject.match(/^RE: /) ? email.subject : `RE: ${email.subject}`;
            const replyMessageBody = `\n \nOn ${email.timestamp}, ${email.sender} wrote:\n${email.body}`;

            compose_email();

            document.querySelector('#compose-recipients').value = email.sender;
            document.querySelector('#compose-subject').value = replySubject;
            document.querySelector('#compose-body').value = replyMessageBody;

            document.querySelector('textarea').addEventListener('focus', (event) => {
                event.target.setSelectionRange(0, 0);
            });
            document.querySelector('textarea').focus();
        });
    }

    const archiveBtn = document.querySelector('#email-archive-btn');
    archiveBtn.replaceWith(archiveBtn.cloneNode(true));
    const newArchiveBtn = document.querySelector('#email-archive-btn');
    newArchiveBtn.style.display = 'block';
    newArchiveBtn.innerHTML = email.archived ? 'Unarchive' : 'Archive';
    newArchiveBtn.addEventListener('click', async () => {
        await toggle_archive(emailId);
        load_mailbox('inbox');
    });

    if (email.id) mark_read(emailId);
}

function get_email(emailId) {
    return fetch(`/emails/${emailId}`).then((response) => response.json());
}

function mark_read(emailId) {
    fetch(`/emails/${emailId}`, {
        method: 'PUT',
        body: JSON.stringify({
            read: true,
        }),
    });
}

async function toggle_archive(emailId) {
    const email = await get_email(emailId);

    await fetch(`/emails/${emailId}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: !email.archived,
        }),
    });
}
