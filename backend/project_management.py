from datetime import datetime

# PROJECT

class Project:
    def __init__(self, project_id, title, description, budget):
        self.project_id = project_id
        self.title = title
        self.description = description
        self.budget = budget

        self.status = "OPEN"

        self.proposals = []
        self.expert = None
        self.project_reviews = []

    def update_project(self, title=None, description=None, budget=None):
        if title:
            self.title = title

        if description:
            self.description = description

        if budget:
            self.budget = budget

    def update_status(self, status):
        valid_status = [
            "OPEN",
            "IN_PROGRESS",
            "COMPLETED",
            "CANCELLED"
        ]

        if status in valid_status:
            self.status = status

    def add_proposal(self, proposal):
        self.proposals.append(proposal)


# PROPOSAL
class Proposal:
    def __init__(
        self,
        proposal_id,
        proposer,
        price,
        duration_days,
        status="PENDING"
    ):
        self.proposal_id = proposal_id
        self.proposer = proposer
        self.price = price
        self.duration_days = duration_days
        self.status = status
        self.created_at = datetime.now()


class ProposalManager:

    def submit_proposal(self, project, proposal):
        if project.status != "OPEN":
            print("Project is not open for proposals")
            return

        project.add_proposal(proposal)

    def get_all_proposals(self, project):
        return project.proposals

    def get_best_proposal(self, project):
        if not project.proposals:
            return None

        return min(
            project.proposals,
            key=lambda p: (p.price, p.duration_days)
        )

    def accept_proposal(self, proposal):
        proposal.status = "ACCEPTED"


# EXPERT
class Expert:
    def __init__(self, expert_id, name, skill):
        self.expert_id = expert_id
        self.name = name
        self.skill = skill
        self.ratings = []

    def average_rating(self):
        if not self.ratings:
            return 0

        return sum(self.ratings) / len(self.ratings)


# HIRE EXPERT
class HireExpertService:

    @staticmethod
    def hire_expert(project, expert):
        if project.status != "OPEN":
            print("Cannot hire expert")
            return False

        project.expert = expert
        project.update_status("IN_PROGRESS")

        return True


# REVIEW
class ExpertReview:
    def __init__(self, score, comment):
        self.score = score
        self.comment = comment


class ProjectReview:
    def __init__(self, score, comment):
        self.score = score
        self.comment = comment


class ReviewService:

    @staticmethod
    def review_expert(expert, review):
        if 1 <= review.score <= 5:
            expert.ratings.append(review.score)

    @staticmethod
    def review_project(project, review):
        if project.status == "COMPLETED":
            project.project_reviews.append(review)


# WORKFLOW
class ProjectWorkflow:

    @staticmethod
    def complete_project(project):
        project.update_status("COMPLETED")

    @staticmethod
    def cancel_project(project):
        project.update_status("CANCELLED")


# DEMO
if __name__ == "__main__":

    # Create Project
    project = Project(
        1,
        "AI Chatbot",
        "Customer Support AI",
        5000
    )

    # Update Project
    project.update_project(
        description="Advanced Customer Support AI",
        budget=6000
    )

    # Proposal Management
    pm = ProposalManager()

    pm.submit_proposal(
        project,
        Proposal(
            1,
            "AI Expert Team",
            4500,
            30
        )
    )

    pm.submit_proposal(
        project,
        Proposal(
            2,
            "Machine Learning Pro",
            4200,
            25
        )
    )

    best_proposal = pm.get_best_proposal(project)

    if best_proposal:
        pm.accept_proposal(best_proposal)

    # Hire Expert
    expert = Expert(
        101,
        "AI Expert",
        "Machine Learning"
    )

    HireExpertService.hire_expert(
        project,
        expert
    )

    # Complete Project
    ProjectWorkflow.complete_project(project)

    # Reviews
    ReviewService.review_expert(
        expert,
        ExpertReview(
            5,
            "Excellent performance"
        )
    )

    ReviewService.review_project(
        project,
        ProjectReview(
            5,
            "Project completed successfully"
        )
    )

    # Output
    print("\n===== PROJECT INFORMATION =====")
    print("PROJECT:", project.title)
    print("DESCRIPTION:", project.description)
    print("BUDGET:", project.budget)
    print("STATUS:", project.status)

    print("\n===== EXPERT INFORMATION =====")
    print("EXPERT:", project.expert.name)
    print("SKILL:", project.expert.skill)
    print("AVG EXPERT RATING:", expert.average_rating())

    print("\n===== PROPOSAL LIST =====")

    for proposal in pm.get_all_proposals(project):
        print(
            proposal.proposer,
            "- Price:", proposal.price,
            "- Duration:", proposal.duration_days,
            "days",
            "- Status:", proposal.status
        )

    print("\nBEST PROPOSAL:")
    print(
        best_proposal.proposer,
        "- Price:", best_proposal.price
    )

    print("\n===== PROJECT REVIEWS =====")

    for review in project.project_reviews:
        print(
            "SCORE:", review.score,
            "| COMMENT:", review.comment
        )

    print("\nTOTAL PROPOSALS:", len(project.proposals))