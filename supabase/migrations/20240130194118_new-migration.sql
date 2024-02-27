create table
  contacts (
    contactid text not null,
    created_at timestamp with time zone not null default now(),
    firstname text null,
    lastname text null,
    companyname text null,
    status text null,
    type text null,
    commodities text null,
    contact_phone text not null,
    contact_email text null,
    followup_count text null,
    last_contact_date timestamp with time zone null default now(),
    growing_method text null,
    need_availability text null,
    campaign text null,
    account_executive text null,
    custom_data json null,
    initial_message_last_contact_date text null,
    gepeto_switch boolean null default true,
    constraint contacts_pkey primary key (contactid),
    constraint contacts_contactid_key unique (contactid)
  );

create table
  bots (
    id text not null,
    created_at timestamp with time zone not null default now(),
    prompt text null,
    confirmation_message text null,
    followup_message text null,
    initial_text text null,
    constraint bots_pkey primary key (id)
  );

create table
messages (
    contactid text null,
    org_phone text null,
    contact_phone text null,
    body text null,
    created_at timestamp with time zone not null default now(),
    direction text null,
    uuid uuid not null default gen_random_uuid (),
    model text null,
    prompt_tokens text null,
    completion_tokens text null,
    type text null,
    campaign text null,
    constraint messages_pkey primary key (uuid)
  );


