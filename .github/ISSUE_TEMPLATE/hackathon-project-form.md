name: Brainhack Project Form
description: This provides the backbone structure for your project description. Please follow along to submit your project!
title: "<My Project Name>"
labels: ["Hackathon project"]
assignees:
  - octocat
body:
  - type: markdown
    attributes:
      value: |
        *We are very excited to meet you at the 2022 OHBM Brainhack 🎉* *To submit a project, you need to be an attendee of the 2022 OHBM Brainhack. We ask you to register first over [here](http://www.humanbrainmapping.org/HackathonReg/). Thank you!*
        
        *We have prepared this template to help with your project submission. Here is how to proceed:*
         1. *Before fill the template check [the guideline](https://github.com/ohbm/hackathon2022/blob/main/.github/ISSUE_TEMPLATE/handbooks/projects.md). Be sure to include as many information as possible*
         2. *Submit the issue*
         3. *Check items in the checklist*
         4. *Once you are done (at least all 'required' items must be provided), please delete the "Guidelines" section add a comment saying 'hi @ohbm/project-monitors: My project is ready!'*

        Thank you!

        *After submission, we will assign a 'project monitor' to follow your submission. If at any time you need help or anything is unclear, please add a comment and ping your project monitor. Our team is here to help!*
        
  - type: input
    id: title
    attributes:
      label: Title
      description: Name of your awesome project. Please also update the title of the issue to be the title of your project
    validations:
      required: true
      
  - type: textarea
    id: project-leads
    attributes:
      label: Project lead
      description: Your name and GitHub login, possibly more than 1 lead
      placeholder: One per line
    validations:
      required: true
      
  - type: dropdown
    id: hub
    attributes:
      label: Hub
      description: The Hackathon Hub your availability fits better.
      options:
        - Glasgow
        - Asia / Pacific
        - Europe / Middle East / Africa
        - Americas
    validations:
      required: true

  - type: input
    id: link
    attributes:
      label: Link to Project
    validations:
      required: false

  - type: input
    id: goals
    attributes:
      label: Goals for the OHBM BrainHack
    validations:
      required: true
      
  - type: textarea
    id: skills
    attributes:
      label: Skills
    validations:
      required: true
      
  - type: input
    id: website-image
    attributes:
      label: Image for the OHBM brainhack website
    validations:
      required: true
      
  - type: markdown
    attributes:
      value: |
        ## Project submission

        ## Submission checklist
        *Once the issue is submitted, please check items in this list as you add under 'Additional project info'*

  - type: checkboxes
    id: checklist
    attributes:
      label: '⠀'
      description: Please include the following above (all required)
      options:
        - label: I agree to follow this project's Code of Conduct
          required: true

  - type: checkboxes
    id: checklist-required
    attributes:
      label: '⠀'
      description: Please include the following above (all required)
      options:
        - label: 'Link to your project: could be a code repository, a shared document, etc. See [here](https://github.com/ohbm/hackathon2022/blob/master/.github/ISSUE_TEMPLATE/handbooks/projects.md#link-to-project)'
        - label: 'Include your [Mattermost handle](https://mattermost.brainhack.org/) (i.e. your username). If you do not have an account, please [sign up here](https://mattermost.brainhack.org/signup_email).'
        - label: 'Goals for the OHBM Brainhack: describe what you want to achieve during this brainhack. See [here](https://github.com/ohbm/hackathon2022/blob/master/.github/ISSUE_TEMPLATE/handbooks/projects.md#goals).'
        - label: 'Flesh out at least 2 "good first issues": those are tasks that do not require any prior knowledge about your project, could be defined as issues in a GitHub repository, or in a shared document, cf [here](https://github.com/ohbm/hackathon2022/blob/master/.github/ISSUE_TEMPLATE/handbooks/projects.md#onboarding-2-good-first-issues).'
        - label: 'Skills: list skills that would be particularly suitable for your project. We ask you to include at least one non-coding skill, cf. [here](https://github.com/ohbm/hackathon2022/blob/master/.github/ISSUE_TEMPLATE/handbooks/projects.md#onboarding-skills).'
        - label: 'Chat channel: A link to a chat channel that will be used during the OHBM Brainhack. This can be an existing channel or a new one. We recommend using the [Brainhack space on mattermost](https://mattermost.brainhack.org/), cf. [here](https://github.com/ohbm/hackathon2022/blob/master/.github/ISSUE_TEMPLATE/handbooks/projects.md#chat).'
        - label: 'Provide an image of your project for the OHBM brainhack website'

  - type: checkboxes
    id: checklist-optional
    attributes:
      label: '⠀'
      description: You can also include information about (all optional)
      options:
        - label: 'Someone co-leading the project in the timeslot you have not selected to provide additional visibility.'
        - label: 'Number of participants, cf. [here](https://github.com/ohbm/hackathon2022/blob/master/.github/ISSUE_TEMPLATE/handbooks/projects.md#participant-capacity)'
        - label: 'Twitter-size summary of your project pitch, cf. [here](https://github.com/ohbm/hackathon2022/blob/master/.github/ISSUE_TEMPLATE/handbooks/projects.md#twitter-size-summary-of-your-project-pitch)'
        - label: 'Set up a kanban board on your repository to better divide the work and keep track of things, cf [here](https://github.com/ohbm/hackathon2022/blob/master/.github/ISSUE_TEMPLATE/handbooks/projects.md#set-up-a-kanban-board)'
        - label: 'Project snippet for the OHBM Brainhack website, cf. [here](https://github.com/ohbm/hackathon2022/blob/master/.github/ISSUE_TEMPLATE/handbooks/projects.md#project-snippet-for-the-ohbm-brainhack-website)'
  
  - type: checkboxes
    id: checklist-recommended
    attributes:
      label: '⠀'
      description: We would like to think about how you will credit and onboard new members to your project. We recommend reading references from [this section](https://github.com/ohbm/hackathon2022/blob/master/.github/ISSUE_TEMPLATE/handbooks/projects.md#credit-and-onboarding). If you'd like to share your thoughts with future project participants, you can include information about (recommended)
      options:
        - label: 'Specify how will you acknowledge contributions (e.g. listing members on a contributing page).'
        - label: 'Provide links to onboarding documents if you have some.'
  
  - type: checkboxes
    id: checklist-qmenta
    attributes:
      label: '⠀'
      description: QMENTA has agreed to sponsor the event and provide computational resources through their platform.
      options:
        - label: 'Get in touch with QMENTA through their [Brain Innovation Hub Slack space](https://brain-innovation-hub.slack.com), if you think your project would benefit from their support.'