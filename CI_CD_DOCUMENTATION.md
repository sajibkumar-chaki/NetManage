# Testing and source delivery

The current V2 main revision is dc7aac3, merged through PR 6 after Sajib's
changes-requested review and approval. Both jobs in main workflow run
40114162713 succeeded. The repository is private and all four members have
access. A fresh Windows run with Python 3.12.14 and pytest 8.4.2 passes all
79 tests, including Qt integration. Qt tests use an offscreen platform.

## Delivery refinement
The revised workflow runs on every push, main pull request and manual dispatch.
It preserves Ubuntu Python 3.12 backend tests and Windows Python 3.13 desktop
tests, saves JUnit XML, then packages source only when both jobs succeed.
The downloadable source artifact has an empty inventory. This is automated
source delivery, not deployment to production routers or a rebuilt executable.
Run python scripts/build_release.py to reproduce the archive locally.

## Merge restriction remains an owner action
The GitHub API reports main as unprotected. The repository plan does not
support the requested rules for this private repository. Sajib is admin;
Mashfiq has write access. The owner must enable a suitable plan and require
checks test and windows-desktop and a genuine approving review. Do not make
the private repository public merely to bypass this plan limitation.
A failing workflow prevents the package job. It does not itself block merging.

## Reproduce
python -m pip install -r requirements.txt -r requirements-desktop.txt
python -m pytest -v
python scripts/build_release.py

## References
https://github.com/sajibkumar-chaki/NetManage/pull/6
https://github.com/sajibkumar-chaki/NetManage/actions/runs/40114162713
https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
