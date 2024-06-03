def extract_common_prefix(accounts):
    # Initialize the common prefix with the first account
    common_prefix = accounts[0]

    # Iterate over the remaining accounts
    for account in accounts[1:]:
        # Find the length of the common prefix
        prefix_length = 0
        while prefix_length < len(common_prefix) and prefix_length < len(account) and common_prefix[prefix_length] == account[prefix_length]:
            prefix_length += 1

        # Update the common prefix
        common_prefix = common_prefix[:prefix_length]

    return common_prefix

# Given list of accounts
accounts = [
    "lfillion@babson.edu.govgplus",
    "lfillion@babson.edu.govcommonidentity",
    "lfillion@babson.edu.govwebex"
]

# Extract the common prefix
result = extract_common_prefix(accounts)

# Print the result
print(f"The common prefix from the accounts is: {result}")


