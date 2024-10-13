# You will receive two items in Data:

	1.	State: The specific state for which tax law changes are being investigated (e.g., “PA”). Use this state abbreviation.
	2.	Context: Scraped data from a website about upcoming tax changes for various states.

--------------
# Task:
Your task is to analyze this context and determine if any of the upcoming tax law changes for the given state correspond to the following tax categories and subcategories:

--------------
# Categories and Subcategories:

	Payroll Taxes

		- Unemployment Compensation (UC) Tax: UC taxable wages, employer contributions, Pennsylvania UC Fund
		- Workers’ Compensation Assessment: Workers’ compensation, payroll assessments, experience rating
		- Pennsylvania UC Withholding: Employee contributions, UC taxable wages, 0.06% rate

	Dependent and Family-Related Tax Credits

		- Personal Income Tax Credit for Dependents: Dependent care expenses, child tax credit, qualifying dependents
		- Child Care Contribution Tax Credit: Employer child care contributions, tax incentives, dependent care

	Retirement and Pension Income

		- Employee Retirement Contributions: 401(k) contributions, Roth IRA, employer retirement plans, tax-deferred
		- Pension and Retirement Income Tax Exclusion: Pension payments, annuities, retirement age, income tax exclusion

	Medical Savings Accounts

		- Health Savings Accounts (HSA): Pre-tax contributions, qualified medical expenses, employer HSA contributions
		- Medical Savings Account (MSA): Employer MSA contributions, medical reimbursement, tax-exempt

	Employee Benefits and Fringe Benefits

		- Cafeteria Plans (Section 125): Pre-tax benefits, flexible spending accounts (FSA), health insurance premiums
		- Employer-Provided Transportation Benefits: Commuter benefits, transit passes, parking benefits, tax exclusions

	Stock Options and Employee Ownership

		- Nonqualified Stock Options (NSOs): NSO income, exercise price, W-2 reporting, payroll tax withholding
		- Incentive Stock Options (ISOs): ISO exercise, alternative minimum tax (AMT), stock grants

	Educational Assistance Programs

		- Tuition Reimbursement Programs: Employee tuition benefits, educational assistance, non-taxable reimbursement
		- Student Loan Repayment Assistance: Employer-provided student loan payments, tax-free benefit

	Temporary Disability Benefits

		- Short-Term Disability Benefits: Short-term disability income, taxable vs. non-taxable benefits
		- Long-Term Disability Benefits: Long-term disability, payroll deductions, tax implications

	Mileage and Vehicle Reimbursements

		- Employee Business Expense Reimbursement: Mileage rates, vehicle use, non-taxable reimbursement

	Garnishments and Wage Attachments

		- Child Support Withholding: Child support orders, payroll deductions, income withholding
		- Tax Levies and Wage Garnishments: IRS tax levy, state tax liens, wage attachments

	Instructions:

		1.	Carefully read the “Tax Changes” for the specified state.
		2.  Replace state with the actual state abbreviation passed as State.
		3.	Compare the tax changes against the defined categories and subcategories above.
		4.	For each match you find, create a JSON object capturing the following details:
		- category: The main category that the tax change belongs to.
		- subcategory: The specific subcategory (if applicable).
		- rationale: A brief explanation of why you believe this tax change matches the category/subcategory.
		- confidence: An integer (1-100) indicating your confidence in the accuracy of the match.
		- is_match: Set this to true if a match is found; otherwise, false.

	Output Format

	Return a JSON document formatted as follows:
	{
	"state": "PA",
	"category": "Payroll Taxes",
	"subcategory": "Unemployment Compensation (UC) Tax",
	"rationale": "The upcoming change affects the unemployment compensation tax rate in PA, which aligns with this category.",
	"confidence": 90,
	"is_match": true,
	"created_at": "",
	}

	If multiple changes match different categories, provide separate JSON objects within an array.

	Example Output When Multiple Matches Are Found:
	[
	{
		"state": "MA",
		"category": "Payroll Taxes",
		"subcategory": "Unemployment Compensation (UC) Tax",
		"rationale": "The upcoming change affects the unemployment compensation tax rate in PA, which aligns with this category.",
		"confidence": 90,
		"is_match": true,
		"created_at": ""
	},
	{
		"state": "MA",
		"category": "Dependent and Family-Related Tax Credits",
		"subcategory": "Child Care Contribution Tax Credit",
		"rationale": "The tax change provides incentives for employer child care contributions, which matches this subcategory.",
		"confidence": 85,
		"is_match": true,
		"created_at": ""
	}
	]

	Example Output When No Match Is Found:
	{
	"state": "CA",
	"category": "",
	"subcategory": "",
	"rationale": "No tax law changes found that match the defined categories.",
	"confidence": 0,
	"is_match": false,
	"created_at": ""
	}

	Important Notes:

		- Ensure the output is in valid JSON format.
		- Always return the full set of parameters in the JSON, even if there is no match.
		- Provide concise yet clear rationales for each match.

	Final Reminder
	Your response must strictly adhere to JSON formatting. Any deviation from this format will be considered incorrect.


--------------
# Data:
State: {state}

Context: {context}