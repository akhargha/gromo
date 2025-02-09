import {
  Navbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  Link,
  DropdownItem,
  DropdownTrigger,
  Dropdown,
  DropdownMenu,
  Avatar,
  Button,
} from "@heroui/react";


export default function NavbarTop() {
  // Get the current path
  const currentPath = window.location.pathname;

  return (
    <Navbar shouldHideOnScroll className="border-b-4 border-green-200 dark:border-green-400">
      <NavbarBrand>
        <p
          style={{
            color: "#25a100",
            fontSize: "35px",
            WebkitTextStroke: "1px black", // Black outline for WebKit browsers
            textShadow: "1px 1px 2px black", // Fallback for better browser support
            paddingBottom: "10px"
          }}
          className="font-bold text-inherit"
        >
          gromo
        </p>
      </NavbarBrand>
      <NavbarContent justify="end" className="flex gap-8">
        {/* Home Link */}
        <NavbarItem isActive={currentPath === "/"}>
          <Link
            style={{
              color: currentPath === "/" ? "#60b048" : "#f0f2f0",
              fontWeight: currentPath === "/" ? "bold" : "normal",
            }}
            href="/"
          >
            Home
          </Link>
        </NavbarItem>

        {/* Investment Link */}
        <NavbarItem isActive={currentPath === "/investment.html"}>
          <Link
            style={{
              color: currentPath === "/investment.html" ? "#60b048" : "#f0f2f0",
              fontWeight: currentPath === "/investment.html" ? "bold" : "normal",
            }}
            href="/investment.html"
          >
            Investment
          </Link>
        </NavbarItem>

        {/* Profile Dropdown */}
        <Dropdown placement="bottom-end">
          <DropdownTrigger>
            <Avatar
              isBordered
              as="button"
              className="transition-transform"
              color="success"
              name="Shash Sunkum"
              size="sm"
              src="https://images.snapwi.re/6b4e/58061908c9e0b29f0a7b23c6.w800.jpg"
            />
          </DropdownTrigger>
          <DropdownMenu aria-label="Profile Actions" variant="flat">
            <DropdownItem key="profile" className="h-14 gap-2">
              <p className="font-semibold">Signed in as</p>
              <p className="font-semibold">shash@gromo.com</p>
            </DropdownItem>
            <DropdownItem key="settings">Settings</DropdownItem>
            <DropdownItem key="help_and_feedback">Help & Feedback</DropdownItem>
            <DropdownItem key="logout" color="danger">
              Log Out
            </DropdownItem>
          </DropdownMenu>
        </Dropdown>
      </NavbarContent>
    </Navbar>
  );
}
