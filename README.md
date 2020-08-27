<!-- Let's throw a row of badges cause never enough of those LOL --->
[![Contributors][contributors-shield]][contributors-url] [![Forks][forks-shield]][forks-url] [![Stargazers][stars-shield]][stars-url] [![Issues][issues-shield]][issues-url] [![MIT License][license-shield]][license-url]
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
    <a href="https://github.com/kablekompany/Kable-Kogs/.github/CONTRIBUTORS">View Contributors</a>
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

- These are "*here, will be here, or are listed* ***with the intent*** to place them here but otherwise I was lazy, forgot, or was looking to get one over on the niche community that would find themselves in this repo", but I digress....

---
| Name | Description |
| --- | --- |
| CustomApps | Core'd from [sauri-cogs](https://github.com/elijabesu/SauriCogs) Application Cog, with expanded customization, and application retrieval. Useful for multi stage vetting process ~~*thanks DMO*~~ |
| Decancer | Hoisters, cancer'r's, or overall nuisance named users hate this cog. Moniker sanitizing from zalgo to char characters I can't even pronounce. Idea from nicknamechanger on [PumCogs Repo](https://github.com/PumPum7/PumCogs). Is a "by user" decancer sanitizing, with custom setups allowing defaulting name, and modlog channel output. |
| KekIDs | Simple cog to 'mass kick' a list of IDs from your server *punts* |
| Sniping | Snipe messages that were deleted in chat. Show your accuracy by passing channel, user, and even a word in the string of the sentence you want to snipe. `sniper` or `sniper list`. Pretty intuitive, with long lasting snipe dict. Catch those shady hoes. `[p]sniper list #general @KableKompany gooch` would return a deleted message stating something about goochal stimulation (Don't Ask)|
| LockItUp | Lockdown cog based off of [SharkyTheKing's](https://github.com/SharkyTheKing/Sharky) `Lockdown`. Allows custom channel lib, config clearing, embed outputs on lock for each channel, and clean text or embed option output on unlock with custom messages, and optional silencer. *Pushing to this repository as the pre-PR write up*
<!--TODO: Add applications, and sniping to repo -->
See the [open issues](https://github.com/kablekompany/Kable-Kogs/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing

Contributions make my Levis Rise; The community surrounding this BotBase is full of Big Brain and overall just cool as fuck people. Learn the code, PR, yell at crayons, and learn some programming!

1. Fork the Project
2. Create your `Feature` Branch (`git checkout -b feature/omegalulCoolAsfFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature and other nonnse for a quippy commit'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`) *followed by a stanky leg*
5. Open a Pull Request (bop it)

**All PRs Welcome — big part of why i decided to publically host some of these**

<!-- LICENSE -->
## License

Distributed under the MIT License. See [LICENSE](https://github.com/kablekompany/kable-kogs/blob/master/LICENSE.txt) for more information.

<!-- CONTACT -->
## Contact

> Trent Kable
[@kablekompany](https://twitter.com/kablekompany) - trent@kablekompany.com
>Project Link:
[https://github.com/kablekompany/Kable-Kogs](https://github.com/kablekompany/Kable-Kogs)

      *click the cool badge things at the top to join my discord server and shit*

## Acknowledgements

Many have contributed to this repo either by proxy, direct interaction, or by some cosmic interference. The contributors in full can be found standalone, and includes __all__ authors that influenced, authored, or has core code within my bot and cogs.

* [Contributors](.github/CONTRIBUTORS)
  * Shows global contribs and Core Contributions to Kronos
* [KRONOS](https://kable.lol/kronos) 
  * *my modified instance of Red, contains these and many more features*
* [Melmsie](https://github.com/melmsie)
  * Easily my best-friend and continuing push in learning development
* [Aetheryx](https://github.com/aetheryx)
  * uwu qt big brain bitch

Join [The Kompound](https://kable.lol/discord) to get insulted, and ask for assistance if you need.

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
[product-screenshot]: images/screenshot.png
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
