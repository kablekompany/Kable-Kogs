### DISCLAIMER

:warning: This repo is not an approved plugin-repo from [CogBoard](cogboard.red/ "Click me BRO!") at this time
> *Install at your own risk, and you assume any liability*

<!-- Let's throw a row of badges cause never enough of those LOL --->
[![Contributors][contributors-shield]][contributors-url] [![Forks][forks-shield]][forks-url] [![Stargazers][stars-shield]][stars-url] [![Issues][issues-shield]][issues-url] [![MIT License][license-shield]][license-url]
![CodeQL](https://github.com/kablekompany/Kable-Kogs/workflows/CodeQL/badge.svg)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/kablekompany/Kable-Kogs.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/kablekompany/Kable-Kogs/context:python)
[![Discord Bots](https://top.gg/api/widget/status/632872758665281567.svg)](https://top.gg/bot/632872758665281567)
<br/>

<!-- PROJECT INIT -->
<br />
<p align="center">
  <a href="https://github.com/kablekompany/Kable-Kogs">
    <img src=".github/images/logo.png" alt="Logo" width="300" height="300">
  </a>
  <br/>
      <a href="https://kable.lol/discord">
        <img align="center" src="https://img.shields.io/badge/Discord-KableKompany%230001-7289DA?logo=discord&style=for-the-badgel" />
    </a>
  <h2 align="center">Kable-Kogs</h2>
  <h4><p align="center"> Red DiscordBot V3 Cogs</h2>
      <p align="center">
        <a href="mailto:trent@kablekompany.com">
        <img align="center" src="https://img.shields.io/badge/trent%40kablekompany.com-blue?style=for-the-badge&logo=gmail" />
    </a>
    <br/>
    <a href="https://github.com/kablekompany/Kable-Kogs/blob/master/.github/CONTRIBUTORS.md">View Contributors</a>
    ·
    <a href="https://github.com/kablekompany/Kable-Kogs/issues">Report Bugs</a>
    ·
    <a href="https://github.com/kablekompany/Kable-Kogs/issues">Request Features</a>
</p>

<!-- TABLE OF CONTENTS -->
## Table of Contents

- [Table of Contents](#table-of-contents)
	- [Built With](#built-with)
- [Getting Started](#getting-started)
	- [Prerequisites](#prerequisites)
	- [Installation](#installation)
- [Cog Menu](#cog-menu)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

### Built With

* [Python 3.8](https://www.python.org/downloads/release/python-380/ "Click this bitch")
* [Discord.py 1.4.0+](https://github.com/Rapptz/discord.py "Sexc wrapper uwu")
* [Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot "Red bot that give em blue balls af")

<!-- GETTING STARTED -->
## Getting Started

Reference and Install from the sources above. Please don't judge the code within these cogs too harshly. Learning and growth expands daily, and these should show that overtime too!

### Prerequisites

Once python is installed, make an environment.

* python

```sh
python3.8 -m venv .redenv
```

Modular base of redbot is what these are catered to, make sure you install it too! It's good to learn the documentation over at [Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot) repo

### Installation

1. Activate the environment

```sh
source ~/.redenv/bin/activate
```

2. Install Red DiscordBot

```sh
pip install Red-Discordbot[postgres]
```

*`[postgres]` arg is optional (see documentation for full information on installing redbot)*

3. Install Repo
  --*Invoked from bot within discord:*--

- `[p]repo add Kable-Kogs https://github.com/kablekompany/Kable-Kogs`

  -- Then add the cog you want: --
  - `[p]cog install Kable-Kogs <name_of_cog>`
    -- *redact all formatting caveats, and [p]=prefix* --

## Cog Menu

---
| Name | Description |
| --- | --- |
| allutils | Grab meta, make polls. Bitchin' |
| customapps | Customize Staff apps for your server |
| decancer | Decancer users names removing special and accented chars. `[p]decancerset` to get started if you're already using redbot core modlog |
| kekids | Walk confidently and wear big shoes. |
| lockitup | Lockdown a list of channels, a channel, or the whole server. |

## Contributing

Contributions make my Levis Rise; The community surrounding this BotBase is full of Big Brain and overall just cool as fuck people. Learn the code, PR, yell at crayons, and learn some programming!

1. Fork the Project
2. Create your `Feature` Branch (`git checkout -b feature/omegalulCoolAsfFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature and other nonnse for a quippy commit'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`) *followed by a stanky leg*
5. Open a Pull Request (bop it)

**All PRs Welcome — big part of why I decided to publically host some of these**

<!-- LICENSE -->
## License

Distributed under the MIT License. See [LICENSE](https://github.com/kablekompany/kable-kogs/blob/master/LICENSE.txt) for more information.

<!-- CONTACT -->
## Contact

> Trent Kable
[@kablekompany](https://twitter.com/kablekompany) - trent@kablekompany.com
>Project Link:
[https://github.com/kablekompany/Kable-Kogs](https://github.com/kablekompany/Kable-Kogs)

## Acknowledgements

Many have contributed to this repo either by proxy, direct interaction, or by some cosmic interference. The contributors in full can be found standalone, and includes __all__ authors that influenced, authored, or has core code within my bot and cogs.

* [Contributors](.github/CONTRIBUTORS.md)
  * Shows global contribs and Core Contributions to Kronos
* [Kronos](https://kable.lol/kronos)
  * *my modified instance of Red, contains these and many more features*
* [Melmsie](https://github.com/melmsie)

* [Aetheryx](https://github.com/aetheryx)

Join [The Kompound](https://kable.lol/discord) for support

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/kablekompany/kable-kogs.svg?style=flat-square
[contributors-url]: https://github.com/kablekompany/kable-kogs/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/kablekompany/kable-kogs.svg?style=flat-square
[forks-url]: https://github.com/kablekompany/kable-kogs/network/members
[stars-shield]: https://img.shields.io/github/stars/kablekompany/kable-kogs.svg?style=flat-square
[stars-url]: https://github.com/kablekompany/kable-kogs/stargazers
[issues-shield]: https://img.shields.io/github/issues/kablekompany/kable-kogs.svg?style=flat-square
[issues-url]: https://github.com/kablekompany/kable-kogs/issues
[license-shield]: https://img.shields.io/github/license/kablekompany/kable-kogs.svg?style=flat-square
[license-url]: https://github.com/kablekompany/kable-kogs/blob/master/LICENSE.txt
[KableKompany#0001]: https://img.shields.io/badge/-Discord-black.svg?style=flat-square&logo=discord&colorB=555
[discord-server]: https://kable.lol/discord
<!-- Mark down build up inspired by https://github.com/othneildrew/Best-README-Template ---->

<p align="center">
    <a href="https://github.com/anuraghazra/github-readme-stats">
      <img align="center" src="https://github-readme-stats.vercel.app/api/top-langs/?username=kablekompany&show_icons=true&layout=compact&theme=light&count_private=true" />
    </a>
<br/>
    <a href="https://github.com/anuraghazra/github-readme-stats">
        <img align="center" width="500" src="https://github-readme-stats.vercel.app/api?username=kablekompany&show_icons=true&theme=light&count_private=true" />
    </a>
<br/>
  </p>
