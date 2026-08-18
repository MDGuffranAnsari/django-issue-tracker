import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Reporter, Issue, CriticalIssue, LowPriorityIssue


@csrf_exempt
def reporter_list(request):

    if request.method == 'POST':
        data = json.loads(request.body)

        reporter = Reporter(
            id=data['id'],
            name=data['name'],
            email=data['email'],
            team=data['team']
        )

        try:
            reporter.validate()
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)

        with open('reporters.json', 'r') as f:
            reporters = json.load(f)

        reporters.append(reporter.to_dict())

        with open('reporters.json', 'w') as f:
            json.dump(reporters, f, indent=2)

        return JsonResponse(reporter.to_dict(), status=201)

    elif request.method == 'GET':

        with open('reporters.json', 'r') as f:
            reporters = json.load(f)

        reporter_id = request.GET.get('id')

        if reporter_id:
            for r in reporters:
                if r['id'] == int(reporter_id):
                    return JsonResponse(r, status=200)

            return JsonResponse(
                {'error': 'Reporter not found'},
                status=404
            )

        return JsonResponse(
            reporters,
            safe=False,
            status=200
        )


@csrf_exempt
def issue_list(request):

    # GET all issues / GET by ID / GET by status
    if request.method == 'GET':

        with open('issues.json', 'r') as f:
            issues = json.load(f)

        issue_id = request.GET.get('id')
        status = request.GET.get('status')

        # GET by ID
        if issue_id:
            for issue in issues:
                if str(issue['id']) == str(issue_id):
                    return JsonResponse(issue, status=200)

            return JsonResponse(
                {'error': 'Issue not found'},
                status=404
            )

        # GET by status
        if status:
            filtered_issues = [
                issue for issue in issues
                if issue['status'].lower() == status.lower()
            ]

            return JsonResponse(
                filtered_issues,
                safe=False,
                status=200
            )

        # GET all
        return JsonResponse(
            issues,
            safe=False,
            status=200
        )

    # POST create issue
    elif request.method == 'POST':

        try:
            data = json.loads(request.body)

            issue_id = data['id']
            title = data['title']
            description = data.get('description', '')
            status = data['status']
            priority = data['priority']
            reporter_id = data['reporter_id']

            # Select the correct subclass
            if priority.lower() == 'critical':

                issue = CriticalIssue(
                    id=issue_id,
                    title=title,
                    description=description,
                    status=status,
                    priority=priority,
                    reporter_id=reporter_id
                )

            elif priority.lower() == 'low':

                issue = LowPriorityIssue(
                    id=issue_id,
                    title=title,
                    description=description,
                    status=status,
                    priority=priority,
                    reporter_id=reporter_id
                )

            else:

                issue = Issue(
                    id=issue_id,
                    title=title,
                    description=description,
                    status=status,
                    priority=priority,
                    reporter_id=reporter_id
                )

            # Validate the issue
            issue.validate()

            # Read existing issues
            with open('issues.json', 'r') as f:
                issues = json.load(f)

            # Save the new issue
            issues.append(issue.to_dict())

            with open('issues.json', 'w') as f:
                json.dump(issues, f, indent=2)

            response_data = issue.to_dict()
            response_data['message'] = issue.describe()

            return JsonResponse(
                response_data,
                status=201
            )

        except ValueError as e:
            return JsonResponse(
                {'error': str(e)},
                status=400
            )

        except KeyError as e:
            return JsonResponse(
                {'error': f'Missing field: {e.args[0]}'},
                status=400
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Invalid JSON'},
                status=400
            )

    return JsonResponse(
        {'error': 'Method not allowed'},
        status=405
    )