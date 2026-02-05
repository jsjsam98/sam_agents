require("dotenv").config("./env");

// All config from .env (no defaults)
const PB_URL = process.env.PB_URL;
const ADMIN_EMAIL = process.env.ADMIN_EMAIL;
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;

async function deleteCollection(headers, name) {
	const response = await fetch(`${PB_URL}/api/collections/${name}`, {
		method: "DELETE",
		headers,
	});

	if (response.ok) {
		console.log(`   🗑️  ${name} deleted`);
	} else if (response.status === 404) {
		console.log(`   ⏭️  ${name} does not exist, skipping`);
	} else {
		const error = await response.json();
		console.log(`   ⚠️  Failed to delete ${name}: ${error.message}`);
	}
}
async function createCollection(headers, collectionData) {
	const response = await fetch(`${PB_URL}/api/collections`, {
		method: "POST",
		headers,
		body: JSON.stringify(collectionData),
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(
			`Failed to create ${collectionData.name}: ${JSON.stringify(error)}`,
		);
	}

	console.log(`   ✅ ${collectionData.name} created successfully`);
}

async function setup() {
	// 1. Login as admin
	console.log("Logging in as admin...");
	const authResponse = await fetch(
		`${PB_URL}/api/collections/_superusers/auth-with-password`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				identity: ADMIN_EMAIL,
				password: ADMIN_PASSWORD,
			}),
		},
	);

	if (!authResponse.ok) {
		const error = await authResponse.json();
		throw new Error(`Login failed: ${JSON.stringify(error)}`);
	}

	const { token } = await authResponse.json();
	console.log("Login successful");

	const headers = {
		"Content-Type": "application/json",
		Authorization: token,
	};

	// 2. Delete existing custom Collections (in dependency order)
	console.log("🗑️  Cleaning up existing collections...");
	const collectionsToDelete = ["users"];

	for (const name of collectionsToDelete) {
		await deleteCollection(headers, name);
	}

	// 3. Create Collections
	// ========== users (anonymous users) ==========
	console.log("📦 Creating users collection...");
	await createCollection(headers, {
		name: "users",
		type: "auth",
		fields: [
			{
				name: "username",
				type: "text",
				required: false,
				max: 50,
			},
			{
				name: "last_active",
				type: "date",
				required: false,
			},
			{
				name: "openai_key",
				type: "text",
				required: false,
				max: 200,
			},
		],
		passwordAuth: {
			enabled: true,
			identityFields: ["email"],
		},
		oauth2: {
			enabled: false,
		},
		// API Rules
		listRule: "", // Anyone can list users
		viewRule: "", // Anyone can view users
		createRule: "", // Anyone can register
		updateRule: "id = @request.auth.id", // Can only update self
		deleteRule: "id = @request.auth.id", // Can only delete self
	});

	// Get users collection ID
	const usersResponse = await fetch(`${PB_URL}/api/collections/users`, {
		headers,
	});
	const usersData = await usersResponse.json();
	const usersCollectionId = usersData.id;
}

setup().catch((err) => {
	console.error("Setup failed:", err.message);
	process.exit(1);
});
