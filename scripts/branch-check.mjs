import { execSync } from 'node:child_process';

const PROTECTED_BRANCHES = ['main'];

try {
	const currentBranch = execSync('git rev-parse --abbrev-ref HEAD', {
		encoding: 'utf-8',
	}).trim();

	if (PROTECTED_BRANCHES.includes(currentBranch)) {
		console.error(`\n❌ DIRECT COMMIT BLOCKED`);
		console.error(`You are on protected branch '${currentBranch}'.`);
		console.error(`Please create a feature branch before committing.\n`);
		process.exit(1);
	}
} catch (error) {
	if (error.status === 1) {
		process.exit(1);
	}
	console.error('Failed to verify git branch:', error.message);
	process.exit(1);
}
