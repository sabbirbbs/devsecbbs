import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base.settings")
django.setup()


from Blog.models import Category
category = [
  {
    "category": "Artificial Intelligence",
    "child_categories": [
      "Machine Learning",
      "Deep Learning",
      "Computer Vision",
      "Natural Language Processing",
      "Robotics"
    ]
  },
  {
    "category": "Programming Languages",
    "child_categories": [
      "Java",
      "Python",
      "C++",
      "Ruby"
    ]
  },
  {
    "category": "Operating Systems",
    "child_categories": [
      "Windows",
      "macOS",
      "Linux",
      "Chrome OS",
      "Android"
    ]
  },
  {
    "category": "Web Development",
    "child_categories": [
      "HTML",
      "CSS",
      "JavaScript",
      "React",
      "Angular"
    ]
  },
  {
    "category": "Databases",
    "child_categories": [
      "MySQL",
      "PostgreSQL",
      "MongoDB",
      "Oracle",
      "SQL Server"
    ]
  },
  {
    "category": "Cloud Computing",
    "child_categories": [
      "AWS",
      "Azure",
      "Google Cloud",
      "Heroku",
      "Alibaba Cloud"
    ]
  },
  {
    "category": "Cybersecurity",
    "child_categories": [
      "Encryption",
      "Firewall",
      "Penetration Testing",
      "Identity and Access Management",
      "Threat Intelligence"
    ]
  },
  {
    "category": "DevOps",
    "child_categories": [
      "Continuous Integration",
      "Continuous Deployment",
      "Infrastructure as Code",
      "Containerization",
      "Microservices"
    ]
  },
  {
    "category": "Mobile Development",
    "child_categories": [
      "iOS Development",
      "Android Development",
      "React Native",
      "Flutter",
      "Xamarin"
    ]
  },
  {
    "category": "Virtual Reality",
    "child_categories": [
      "Augmented Reality",
      "VR Headset",
      "VR Gaming",
      "VR Training",
      "VR Therapy"
    ]
  },
  {
    "category": "Gaming",
    "child_categories": [
      "PC Gaming",
      "Console Gaming",
      "Mobile Gaming",
      "Esports",
      "VR Gaming"
    ]
  },
  {
    "category": "Blockchain",
    "child_categories": [
      "Cryptocurrency",
      "Smart Contracts",
      "Decentralized Applications",
      "Distributed Ledger Technology",
      "Blockchain Gaming"
    ]
  },
  {
    "category": "Internet of Things",
    "child_categories": [
      "Smart Home Devices",
      "Wearable Devices",
    ]
  }
]

print(Category.objects.all())


for x in range(1,len(category)):
  print(category[x]['category'])
  try:
    root = Category.objects.create(name=category[x]['category'])
  except:
    pass
  for y in category[x]['child_categories']:
    try:
      Category.objects.create(name=y,parent=root)
    except:
      pass
    print("--> "+y)
